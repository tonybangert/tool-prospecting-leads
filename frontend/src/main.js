import {
  fetchKpis,
  fetchSubscribers,
  fetchChurn,
  fetchSegments,
  fetchRecommendations,
  fetchRevenueForecast,
  fetchRetentionActions,
} from "./utils/api.js";

import { renderKpiBar } from "./components/kpi-bar.js";
import { renderSubscriberOverview } from "./components/subscriber-overview.js";
import { renderChurnPrediction } from "./components/churn-prediction.js";
import { renderSmartSegments } from "./components/smart-segments.js";
import { renderRecommendations } from "./components/recommendations.js";
import { renderRevenueForecast } from "./components/revenue-forecast.js";
import { renderRetentionActions } from "./components/retention-actions.js";
import { renderTicker } from "./components/ticker.js";
import { renderProspectSearch } from "./components/prospect-search.js";

async function initDashboard() {
  const results = await Promise.allSettled([
    fetchKpis(),
    fetchSubscribers(),
    fetchChurn(),
    fetchSegments(),
    fetchRecommendations(),
    fetchRevenueForecast(),
    fetchRetentionActions(),
  ]);

  // Render stock ticker strip from KPI data
  if (results[0].status === "fulfilled") {
    renderTicker(results[0].value, document.getElementById("ticker"));
  }

  const renderers = [
    { result: results[0], render: renderKpiBar, id: "kpi-bar" },
    { result: results[1], render: renderSubscriberOverview, id: "subscriber-overview" },
    { result: results[2], render: renderChurnPrediction, id: "churn-prediction" },
    { result: results[3], render: renderSmartSegments, id: "smart-segments" },
    { result: results[4], render: renderRecommendations, id: "recommendations" },
    { result: results[5], render: renderRevenueForecast, id: "revenue-forecast" },
    { result: results[6], render: renderRetentionActions, id: "retention-actions" },
  ];

  // Render prospect search (standalone — doesn't need API data to initialize)
  renderProspectSearch(document.getElementById("prospect-search"));

  renderers.forEach(({ result, render, id }) => {
    const section = document.getElementById(id);
    if (result.status === "fulfilled") {
      render(result.value, section);
      section.classList.add("loaded");
    } else {
      section.innerHTML = `<div class="section-error">Failed to load section: ${result.reason?.message ?? "Unknown error"}</div>`;
    }
  });
}

initDashboard();
