import { useState, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import Header from "./components/Header";
import DashboardHub from "./components/DashboardHub";
import TabBar from "./components/TabBar";
import IcpModelList from "./components/IcpModelList";
import ProspectPipeline from "./components/ProspectPipeline";
import Footer from "./components/Footer";
import { MOCK_DATA, getGreeting } from "./lib/hub-utils";
import { fetchSlackMessages, fetchGoogleDriveFiles } from "./lib/api";

type View = "hub" | "models" | "prospects";

const TOOL_TABS = [
  { key: "models", label: "ICP Models" },
  { key: "prospects", label: "Prospect Pipeline" },
];

export default function App() {
  const [view, setView] = useState<View>("hub");
  const [activeTab, setActiveTab] = useState("models");
  const [prospectModelId, setProspectModelId] = useState<string | null>(null);

  const { data: slackData, isLoading: slackLoading } = useQuery({
    queryKey: ["slack-messages"],
    queryFn: fetchSlackMessages,
    refetchInterval: 60_000,
  });

  const { data: googleData, isLoading: googleLoading } = useQuery({
    queryKey: ["google-drive-files"],
    queryFn: fetchGoogleDriveFiles,
    refetchInterval: 120_000,
  });

  const slackError = slackData?.error ?? null;
  const googleError = googleData?.error ?? null;

  const hubData = useMemo(() => ({
    ...MOCK_DATA,
    slack: slackData?.messages ?? [],
    googledocs: googleData?.files ?? [],
  }), [slackData, googleData]);

  function handleSearchProspects(modelId: string) {
    setProspectModelId(modelId);
    setActiveTab("prospects");
    setView("prospects");
  }

  return (
    <div className="dashboard-bg">
      <Header onHubClick={() => setView("hub")} showHub={view !== "hub"} />

      <main className="mx-auto max-w-container flex flex-col gap-5 p-6">
        {view === "hub" && (
          <>
            <div className="flex items-center justify-between mb-1">
              <div>
                <h2 className="text-xl font-bold text-navy">{getGreeting(hubData).headline}</h2>
                <p className="text-sm text-muted">{getGreeting(hubData).subtext}</p>
              </div>
              <button
                onClick={() => setView("models")}
                className="text-sm text-navy/70 hover:text-navy border border-navy/15 hover:border-navy/30 px-4 py-2 rounded-lg transition-colors"
              >
                Open Research Tools &rarr;
              </button>
            </div>
            <DashboardHub
              data={hubData}
              slackLoading={slackLoading}
              slackError={slackError}
              googleLoading={googleLoading}
              googleError={googleError}
              googleAuthenticated={googleData?.authenticated ?? false}
              googleAuthUrl={googleData?.authUrl}
              googleAnalysis={googleData?.analysis}
            />
          </>
        )}

        {(view === "models" || view === "prospects") && (
          <>
            <TabBar
              tabs={TOOL_TABS}
              active={activeTab}
              onSelect={(key) => {
                setActiveTab(key);
                setView(key as View);
              }}
            />
            {activeTab === "models" && (
              <IcpModelList onSearchProspects={handleSearchProspects} />
            )}
            {activeTab === "prospects" && (
              <ProspectPipeline initialModelId={prospectModelId} />
            )}
          </>
        )}
      </main>

      <Footer />
    </div>
  );
}
