import { Home } from "lucide-react";

interface Props {
  onHubClick: () => void;
  showHub: boolean;
}

export default function Header({ onHubClick, showHub }: Props) {
  return (
    <header className="bg-navy text-white py-4 px-6 border-b-[3px] border-amber">
      <div className="mx-auto max-w-container flex items-center justify-between">
        <div className="flex items-center gap-3">
          <img src="/logo.png" alt="PerformanceLabs" className="h-8 w-8" />
          <h1 className="text-xl font-bold tracking-tight">PerformanceLabs</h1>
          <span className="bg-amber text-navy text-[0.65rem] font-bold px-2.5 py-1 rounded-[3px] uppercase tracking-wide">
            Prospecting
          </span>
        </div>
        <div className="flex items-center gap-4">
          {showHub && (
            <button
              onClick={onHubClick}
              className="flex items-center gap-1.5 text-sm text-white/70 hover:text-white transition-colors"
            >
              <Home size={14} />
              Hub
            </button>
          )}
          <p className="text-text-light text-sm">ICP-Driven Prospect Research</p>
        </div>
      </div>
    </header>
  );
}
