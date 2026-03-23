import type { PipelineStep } from "../types/api.types";

const STEPS: { key: PipelineStep; label: string }[] = [
  { key: "discover", label: "Discover" },
  { key: "select", label: "Select" },
  { key: "enrich", label: "Enrich" },
  { key: "results", label: "Results" },
];

const ORDER: Record<PipelineStep, number> = {
  discover: 0,
  select: 1,
  enrich: 2,
  results: 3,
};

interface Props {
  current: PipelineStep;
}

export default function StepIndicator({ current }: Props) {
  const currentIdx = ORDER[current];

  return (
    <div className="flex items-center gap-1 mb-6">
      {STEPS.map((step, i) => {
        const isCompleted = i < currentIdx;
        const isActive = i === currentIdx;

        return (
          <div key={step.key} className="flex items-center">
            {i > 0 && (
              <div
                className={`w-8 h-0.5 mx-1 ${
                  isCompleted ? "bg-navy" : "bg-gray-200"
                }`}
              />
            )}
            <div className="flex items-center gap-1.5">
              <div
                className={`w-7 h-7 rounded-full flex items-center justify-center text-[0.7rem] font-bold ${
                  isCompleted
                    ? "bg-navy text-white"
                    : isActive
                      ? "bg-amber text-navy"
                      : "bg-gray-200 text-gray-400"
                }`}
              >
                {isCompleted ? "\u2713" : i + 1}
              </div>
              <span
                className={`text-[0.75rem] font-semibold ${
                  isCompleted
                    ? "text-navy"
                    : isActive
                      ? "text-amber-dark"
                      : "text-gray-400"
                }`}
              >
                {step.label}
              </span>
            </div>
          </div>
        );
      })}
    </div>
  );
}
