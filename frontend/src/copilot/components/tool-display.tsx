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

export const isErrorResult = (result: string | undefined): boolean => {
  if (!result) return false;
  const head = result.slice(0, 96).toLowerCase();
  return (
    head.startsWith("failed ") ||
    head.startsWith("rejected") ||
    head.includes("error: ") ||
    head.includes("invalid ")
  );
};
