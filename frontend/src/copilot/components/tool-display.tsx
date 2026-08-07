import type { ReactNode } from "react";

export const KVRow: React.FC<{ label: string; children: ReactNode }> = ({ label, children }) => (
  <div className="kv-row">
    <span className="kv-label">{label}</span>
    <span className="kv-value">{children}</span>
  </div>
);

export const MutedText: React.FC<{ children: ReactNode }> = ({ children }) => (
  <span className="muted-text">{children}</span>
);

export const ArgsBlock: React.FC<{ args: Record<string, unknown> }> = ({ args }) => (
  <pre className="args-block">{JSON.stringify(args, null, 2)}</pre>
);

// Tool results arrive as plain strings - there is no error flag on the render props -
// so the failure states the backend actually emits are matched by their opening
// words. Only the head is scanned: a long result (a markdown table, a past report)
// can legitimately contain any of these words further down.
const ERROR_MARKERS = [
  "failed",
  "rejected",
  "error: ",
  "invalid ",
  "unavailable",
  "returned no rows",
  "limit reached",
  "exceeding",
  "found issues",
  "unknown table",
  "were found",
  "nothing deleted",
  "no saved report",
];

export const isErrorResult = (result: string | undefined): boolean => {
  if (!result) return false;
  const head = result.slice(0, 160).toLowerCase();
  return ERROR_MARKERS.some((marker) => head.includes(marker));
};
