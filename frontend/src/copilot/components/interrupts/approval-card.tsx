import type { ReactNode } from "react";
import { ArgsBlock, KVRow } from "../tool-display";
import { useInterruptContext } from "./interrupt-context";

function ApprovalCardRoot({ children }: { children: ReactNode }) {
  const {
    state: { resolved },
  } = useInterruptContext();

  if (resolved) {
    return (
      <div className="approval-card approval-resolved" role="status">
        <span>Decision submitted — waiting for agent…</span>
      </div>
    );
  }

  return <div className="approval-card">{children}</div>;
}

function ApprovalCardHeader({ title }: { title: string }) {
  return (
    <div className="approval-header">
      <span>⚠️</span>
      <span>{title}</span>
    </div>
  );
}

function ApprovalCardBody({ children }: { children: ReactNode }) {
  return <div className="approval-body">{children}</div>;
}

function ApprovalCardToolRow() {
  const {
    meta: { action },
  } = useInterruptContext();
  return (
    <KVRow label="Tool">
      <code className="approval-tool-name">{action.name}</code>
    </KVRow>
  );
}

function ApprovalCardArgsSection() {
  const {
    meta: { action },
  } = useInterruptContext();
  return (
    <div className="approval-args">
      <span className="approval-args-label">Arguments</span>
      <ArgsBlock args={action.args ?? {}} />
    </div>
  );
}

function ApprovalCardDefaultActions() {
  const {
    meta: { allowed },
    actions: { approve, reject },
  } = useInterruptContext();

  return (
    <div className="approval-actions">
      {allowed.includes("approve") && (
        <button type="button" className="btn btn-approve" onClick={approve}>
          Approve
        </button>
      )}
      {allowed.includes("reject") && (
        <button type="button" className="btn btn-reject" onClick={reject}>
          Reject
        </button>
      )}
    </div>
  );
}

export const ApprovalCard = {
  Root: ApprovalCardRoot,
  Header: ApprovalCardHeader,
  Body: ApprovalCardBody,
  ToolRow: ApprovalCardToolRow,
  ArgsSection: ApprovalCardArgsSection,
  DefaultActions: ApprovalCardDefaultActions,
};
