const BASE = "/api";

async function fetchJSON(path) {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) throw new Error(`API ${path}: ${res.status}`);
  return res.json();
}

export const fetchKpis = () => fetchJSON("/dashboard/kpis");
export const fetchSubscribers = () => fetchJSON("/subscribers");
export const fetchChurn = () => fetchJSON("/churn");
export const fetchSegments = () => fetchJSON("/segments");
export const fetchRecommendations = () => fetchJSON("/recommendations");
export const fetchRevenueForecast = () => fetchJSON("/revenue-forecast");
export const fetchRetentionActions = () => fetchJSON("/retention-actions");

// ICP + Prospect APIs
export const fetchIcpModels = () => fetchJSON("/icp/");
export const activateIcpModel = (id) =>
  fetch(`${BASE}/icp/${id}/activate`, { method: "POST" }).then((r) => {
    if (!r.ok) throw new Error(`Activate ICP: ${r.status}`);
    return r.json();
  });

export const searchProspects = (modelId, page = 1, perPage = 25) =>
  fetch(`${BASE}/prospects/search/${modelId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ page, per_page: perPage }),
  }).then((r) => {
    if (!r.ok) throw new Error(`Search prospects: ${r.status}`);
    return r.json();
  });

export const listProspects = (modelId, page = 1, perPage = 25) =>
  fetchJSON(`/prospects/${modelId}?page=${page}&per_page=${perPage}`);
