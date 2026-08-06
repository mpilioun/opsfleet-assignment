import { createContext, useContext, type ReactNode } from "react";

export type RenderStatus = "inProgress" | "executing" | "complete";
export type Tone = "neutral" | "info" | "destructive";
export type ToolCardVariant = "default" | "error";

interface ToolCardContextValue {
  tone: Tone;
  variant: ToolCardVariant;
  status: RenderStatus;
}

const ToolCardContext = createContext<ToolCardContextValue | null>(null);

function ToolCardRoot({
  tone = "neutral",
  variant = "default",
  status,
  children,
}: {
  tone?: Tone;
  variant?: ToolCardVariant;
  status: RenderStatus;
  children: ReactNode;
}) {
  return (
    <ToolCardContext.Provider value={{ tone, variant, status }}>
      <div className={`tool-card tool-card-${variant === "error" ? "error" : tone}`}>{children}</div>
    </ToolCardContext.Provider>
  );
}

function ToolCardHeader({ title, children }: { title: string; children?: ReactNode }) {
  const ctx = useContext(ToolCardContext)!;
  return (
    <div className="tool-card-header">
      <div className="tool-card-header-row">
        <span className="tool-card-title">{title}</span>
        <ToolCardStatusBadge status={ctx.status} variant={ctx.variant} />
      </div>
      {children}
    </div>
  );
}

function ToolCardSubtitle({ children }: { children: ReactNode }) {
  return <div className="tool-card-subtitle">{children}</div>;
}

function ToolCardBody({ children }: { children: ReactNode }) {
  return <div className="tool-card-body">{children}</div>;
}

function ToolCardStatusBadge({ status, variant }: { status: RenderStatus; variant: ToolCardVariant }) {
  if (variant === "error") {
    return <span className="status-badge status-error">Failed</span>;
  }
  if (status === "complete") {
    return <span className="status-badge status-complete">Done</span>;
  }
  return <span className="status-badge status-working">Working…</span>;
}

export const ToolCard = {
  Root: ToolCardRoot,
  Header: ToolCardHeader,
  Subtitle: ToolCardSubtitle,
  Body: ToolCardBody,
};
