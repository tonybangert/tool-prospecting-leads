"""Google Drive API routes — OAuth flow, 12-hour activity feed + Claude analysis."""

from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from app.config import settings
from app.schemas.google_drive import GoogleDriveFeedResponse, GoogleDocAnalysis
from app.services.google_drive import GoogleDriveService, analyze_docs_with_claude

router = APIRouter(prefix="/api/google", tags=["google-drive"])


def _get_service() -> GoogleDriveService | None:
    """Return a GoogleDriveService if credentials are configured, else None."""
    if not settings.google_client_id or not settings.google_client_secret:
        return None
    return GoogleDriveService(
        client_id=settings.google_client_id,
        client_secret=settings.google_client_secret,
        redirect_uri=settings.google_redirect_uri,
    )


@router.get("/auth")
async def google_auth():
    """Redirect the user to Google's OAuth consent screen."""
    svc = _get_service()
    if not svc:
        return {"error": "Google Drive not configured"}
    return RedirectResponse(svc.get_auth_url())


@router.get("/callback")
async def google_callback(code: str):
    """Exchange the authorization code for tokens, then redirect to frontend."""
    svc = _get_service()
    if not svc:
        return {"error": "Google Drive not configured"}
    svc.exchange_code(code)
    return RedirectResponse("http://localhost:5173")


@router.get("/files", response_model=GoogleDriveFeedResponse)
async def get_google_files():
    """Return files modified in last 12h with Claude-powered analysis."""
    svc = _get_service()

    # Not configured
    if not svc:
        return GoogleDriveFeedResponse(
            authenticated=False, error="Google Drive not configured"
        )

    # Not authenticated yet
    if not svc.is_authenticated():
        return GoogleDriveFeedResponse(
            authenticated=False, authUrl=svc.get_auth_url()
        )

    # No folder ID
    if not settings.google_drive_folder_id:
        return GoogleDriveFeedResponse(
            authenticated=True, error="No folder ID configured"
        )

    # Fetch recent files (last 12 hours) with content
    try:
        files_with_content = await svc.fetch_files_with_content(
            settings.google_drive_folder_id, hours=12
        )
    except Exception as exc:
        return GoogleDriveFeedResponse(authenticated=True, error=str(exc))

    # Strip content before sending to frontend (it's only for Claude)
    files_for_response = [
        {k: v for k, v in f.items() if k != "content"} for f in files_with_content
    ]

    # Run Claude analysis if we have docs and an API key
    analysis = None
    if files_with_content and settings.anthropic_api_key:
        try:
            raw = await analyze_docs_with_claude(
                files_with_content,
                api_key=settings.anthropic_api_key,
                model=settings.claude_model,
            )
            analysis = GoogleDocAnalysis(**raw)
        except Exception:
            # Analysis is best-effort — don't fail the whole response
            analysis = None

    return GoogleDriveFeedResponse(
        authenticated=True,
        files=files_for_response,
        analysis=analysis,
    )
