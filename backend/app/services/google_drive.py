"""Google Drive integration — OAuth2 flow, 12-hour activity window, Claude analysis."""

import asyncio
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

import anthropic

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
TOKEN_PATH = Path(__file__).resolve().parent.parent.parent / ".google_tokens.json"

# Google Workspace MIME types that can be exported as plain text
EXPORTABLE_MIMES = {
    "application/vnd.google-apps.document": "text/plain",
    "application/vnd.google-apps.spreadsheet": "text/csv",
    "application/vnd.google-apps.presentation": "text/plain",
}


class GoogleDriveService:
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        self._client_config = {
            "web": {
                "client_id": client_id,
                "client_secret": client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [redirect_uri],
            }
        }
        self._redirect_uri = redirect_uri

    def get_auth_url(self) -> str:
        """Build Google OAuth consent URL."""
        flow = Flow.from_client_config(self._client_config, scopes=SCOPES)
        flow.redirect_uri = self._redirect_uri
        url, _ = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent",
        )
        return url

    def exchange_code(self, code: str) -> None:
        """Exchange authorization code for tokens and persist to disk."""
        flow = Flow.from_client_config(self._client_config, scopes=SCOPES)
        flow.redirect_uri = self._redirect_uri
        flow.fetch_token(code=code)
        creds = flow.credentials
        TOKEN_PATH.write_text(creds.to_json())

    def _load_credentials(self) -> Credentials | None:
        """Load stored credentials, auto-refreshing if expired."""
        if not TOKEN_PATH.exists():
            return None
        creds = Credentials.from_authorized_user_info(
            json.loads(TOKEN_PATH.read_text()), SCOPES
        )
        if creds.valid:
            return creds
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            TOKEN_PATH.write_text(creds.to_json())
            return creds
        return None

    def is_authenticated(self) -> bool:
        return self._load_credentials() is not None

    def _list_recent_files_sync(
        self, folder_id: str, hours: int = 12, max_results: int = 20
    ) -> list[dict]:
        """List files modified within the last `hours` hours (sync, run via to_thread)."""
        creds = self._load_credentials()
        if not creds:
            raise RuntimeError("Not authenticated")

        cutoff = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
        service = build("drive", "v3", credentials=creds)
        resp = (
            service.files()
            .list(
                q=(
                    f"'{folder_id}' in parents"
                    f" and trashed = false"
                    f" and modifiedTime > '{cutoff}'"
                ),
                pageSize=max_results,
                fields="files(id, name, mimeType, modifiedTime, lastModifyingUser, webViewLink)",
                orderBy="modifiedTime desc",
            )
            .execute()
        )
        results = []
        for f in resp.get("files", []):
            results.append(
                {
                    "id": f["id"],
                    "name": f["name"],
                    "mimeType": f.get("mimeType", ""),
                    "modifiedTime": f.get("modifiedTime", ""),
                    "modifiedBy": (f.get("lastModifyingUser") or {}).get(
                        "displayName", ""
                    ),
                    "url": f.get("webViewLink", ""),
                }
            )
        return results

    def _export_doc_content_sync(self, file_id: str, mime_type: str) -> str:
        """Export a Google Workspace file as plain text (sync)."""
        creds = self._load_credentials()
        if not creds:
            raise RuntimeError("Not authenticated")
        service = build("drive", "v3", credentials=creds)

        export_mime = EXPORTABLE_MIMES.get(mime_type)
        if export_mime:
            # Google Workspace doc — use export
            content = service.files().export(fileId=file_id, mimeType=export_mime).execute()
            if isinstance(content, bytes):
                return content.decode("utf-8", errors="replace")
            return str(content)
        else:
            # Binary/non-Workspace file — skip content extraction
            return ""

    async def list_recent_files(
        self, folder_id: str, hours: int = 12, max_results: int = 20
    ) -> list[dict]:
        """Async wrapper for listing recent files."""
        return await asyncio.to_thread(
            self._list_recent_files_sync, folder_id, hours, max_results
        )

    async def export_doc_content(self, file_id: str, mime_type: str) -> str:
        """Async wrapper for exporting document content."""
        return await asyncio.to_thread(
            self._export_doc_content_sync, file_id, mime_type
        )

    async def fetch_files_with_content(
        self, folder_id: str, hours: int = 12, max_results: int = 20
    ) -> list[dict]:
        """List recent files and attach truncated content for each exportable doc."""
        files = await self.list_recent_files(folder_id, hours, max_results)

        # Fetch content in parallel for exportable types
        async def attach_content(f: dict) -> dict:
            if f["mimeType"] in EXPORTABLE_MIMES:
                try:
                    content = await self.export_doc_content(f["id"], f["mimeType"])
                    # Truncate to ~4000 chars to stay within Claude context budget
                    f["content"] = content[:4000]
                except Exception:
                    f["content"] = ""
            else:
                f["content"] = ""
            return f

        return await asyncio.gather(*(attach_content(f) for f in files))


async def analyze_docs_with_claude(
    files: list[dict], api_key: str, model: str
) -> dict:
    """Send recent doc summaries to Claude for correlation and to-do extraction.

    Returns: {summary: str, todos: [{text, source, priority}], correlations: [str]}
    """
    if not files:
        return {"summary": "No documents were modified in the last 12 hours.", "todos": [], "correlations": []}

    # Build a digest of each doc for Claude
    doc_digest = []
    for f in files:
        entry = f"### {f['name']}\n- Modified by: {f['modifiedBy']}\n- Modified: {f['modifiedTime']}\n- Type: {f['mimeType']}"
        if f.get("content"):
            entry += f"\n- Content preview:\n{f['content']}"
        doc_digest.append(entry)

    docs_text = "\n\n".join(doc_digest)

    client = anthropic.AsyncAnthropic(api_key=api_key)
    response = await client.messages.create(
        model=model,
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": (
                    "You are an executive assistant analyzing recent Google Drive activity. "
                    "Below are documents modified in the last 12 hours.\n\n"
                    f"{docs_text}\n\n"
                    "Respond with ONLY valid JSON (no markdown fences) with this structure:\n"
                    "{\n"
                    '  "summary": "1-2 sentence overview of recent activity",\n'
                    '  "todos": [{"text": "action item", "source": "doc name", "priority": "high|medium|low"}],\n'
                    '  "correlations": ["insight about how docs relate to each other"]\n'
                    "}\n\n"
                    "Extract concrete action items and to-dos from the document content. "
                    "Identify correlations between documents (shared topics, related projects, "
                    "dependent work). Keep it concise and actionable."
                ),
            }
        ],
    )

    raw = response.content[0].text.strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"summary": raw[:300], "todos": [], "correlations": []}
