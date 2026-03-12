/**
 * Prospect Search component — ICP model selector + Apollo search + scored results table.
 */
import { fetchIcpModels, searchProspects, listProspects, activateIcpModel } from "../utils/api.js";

export function renderProspectSearch(container) {
  container.innerHTML = `
    <div class="section-header">
      <div class="section-number">P</div>
      <div>
        <div class="section-act">Prospecting</div>
        <div class="section-title">ICP Prospect Search</div>
        <div class="section-subtitle">Search Apollo for contacts matching your Ideal Customer Profile</div>
      </div>
    </div>
    <div class="prospect-controls">
      <div class="prospect-select-wrap">
        <label for="icp-select">ICP Model</label>
        <select id="icp-select" class="prospect-select" disabled>
          <option>Loading models...</option>
        </select>
      </div>
      <button id="search-btn" class="prospect-btn" disabled>Search Prospects</button>
      <button id="load-btn" class="prospect-btn prospect-btn-secondary" disabled>Load Saved</button>
    </div>
    <div id="prospect-status" class="prospect-status"></div>
    <div id="prospect-results"></div>
  `;

  let models = [];
  const select = container.querySelector("#icp-select");
  const searchBtn = container.querySelector("#search-btn");
  const loadBtn = container.querySelector("#load-btn");
  const statusEl = container.querySelector("#prospect-status");
  const resultsEl = container.querySelector("#prospect-results");

  // Load ICP models
  fetchIcpModels()
    .then((data) => {
      models = data;
      if (models.length === 0) {
        select.innerHTML = `<option>No ICP models — create one via API first</option>`;
        return;
      }
      select.innerHTML = models
        .map(
          (m) =>
            `<option value="${m.id}" ${m.is_active ? "selected" : ""}>${m.name}${m.is_active ? " (active)" : ""}</option>`
        )
        .join("");
      select.disabled = false;
      searchBtn.disabled = false;
      loadBtn.disabled = false;
    })
    .catch(() => {
      select.innerHTML = `<option>Failed to load models</option>`;
    });

  // Search button
  searchBtn.addEventListener("click", async () => {
    const modelId = select.value;
    if (!modelId) return;

    searchBtn.disabled = true;
    searchBtn.textContent = "Searching...";
    statusEl.innerHTML = `<div class="prospect-loading">Searching Apollo for matching contacts...</div>`;
    resultsEl.innerHTML = "";

    try {
      const data = await searchProspects(modelId);
      statusEl.innerHTML = `<div class="prospect-success">Found ${data.total} prospects</div>`;
      renderResults(data, resultsEl);
    } catch (err) {
      statusEl.innerHTML = `<div class="prospect-error">Search failed: ${err.message}</div>`;
    } finally {
      searchBtn.disabled = false;
      searchBtn.textContent = "Search Prospects";
    }
  });

  // Load saved button
  loadBtn.addEventListener("click", async () => {
    const modelId = select.value;
    if (!modelId) return;

    loadBtn.disabled = true;
    loadBtn.textContent = "Loading...";
    statusEl.innerHTML = "";

    try {
      const data = await listProspects(modelId);
      if (data.total === 0) {
        statusEl.innerHTML = `<div class="prospect-status-msg">No saved prospects. Click "Search Prospects" first.</div>`;
      } else {
        statusEl.innerHTML = `<div class="prospect-success">${data.total} saved prospects</div>`;
      }
      renderResults(data, resultsEl);
    } catch (err) {
      statusEl.innerHTML = `<div class="prospect-error">Load failed: ${err.message}</div>`;
    } finally {
      loadBtn.disabled = false;
      loadBtn.textContent = "Load Saved";
    }
  });

  container.classList.add("loaded");
}

function renderResults(data, el) {
  if (!data.items || data.items.length === 0) {
    el.innerHTML = `<p class="prospect-empty">No prospects to display.</p>`;
    return;
  }

  const rows = data.items
    .map(
      (p) => `
    <tr class="prospect-row">
      <td class="pr-name">${esc(p.first_name || "")} ${esc(p.last_name || "")}</td>
      <td>${esc(p.title || "—")}</td>
      <td>${esc(p.company_name || "—")}</td>
      <td>${esc(p.industry || "—")}</td>
      <td><span class="score-badge ${scoreClass(p.icp_fit_score)}">${fmtScore(p.icp_fit_score)}</span></td>
      <td>${p.linkedin_url ? `<a href="${esc(p.linkedin_url)}" target="_blank" rel="noopener" class="pr-link">LinkedIn</a>` : "—"}</td>
    </tr>
  `
    )
    .join("");

  el.innerHTML = `
    <table class="prospect-table">
      <thead>
        <tr>
          <th>Name</th>
          <th>Title</th>
          <th>Company</th>
          <th>Industry</th>
          <th>ICP Fit</th>
          <th>Profile</th>
        </tr>
      </thead>
      <tbody>${rows}</tbody>
    </table>
  `;
}

function scoreClass(score) {
  if (score == null) return "score-na";
  if (score >= 0.7) return "score-high";
  if (score >= 0.4) return "score-mid";
  return "score-low";
}

function fmtScore(score) {
  if (score == null) return "N/A";
  return `${Math.round(score * 100)}%`;
}

function esc(str) {
  const d = document.createElement("div");
  d.textContent = str;
  return d.innerHTML;
}
