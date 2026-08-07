import React, { createContext, useContext, useMemo, type ReactNode } from "react";
import { CopilotKit, useInterrupt } from "@copilotkit/react-core/v2";

import { AGENT_NAME, COPILOT_RUNTIME_URL } from "../config";
import { ApprovalCard } from "./components/interrupts/approval-card";
import {
  InterruptProvider,
  useInterruptState,
  type Decision,
  type ToolAction,
} from "./components/interrupts/interrupt-context";
import { useRetailToolRenderers } from "./components/tool-renderers";
import { parseInterruptValue } from "./interrupt-utils";
import { useThread } from "./use-thread";

interface AgentContextValue {
  agentName: string;
  threadId: string;
  resetThread: () => string;
}

const AgentContext = createContext<AgentContextValue | null>(null);

const InterruptRenderer: React.FC<{
  action: ToolAction;
  allowed: string[];
  onResolve: (value: { decisions: Decision[] }) => void;
}> = ({ action, allowed, onResolve }) => {
  const { state, actions, meta } = useInterruptState({ action, allowed, onResolve });

  return (
    <InterruptProvider state={state} actions={actions} meta={meta}>
      <ApprovalCard.Root>
        <ApprovalCard.Header title="Confirmation required" />
        <ApprovalCard.Body>
          <ApprovalCard.ToolRow />
          <ApprovalCard.ArgsSection />
          <ApprovalCard.DefaultActions />
        </ApprovalCard.Body>
      </ApprovalCard.Root>
    </InterruptProvider>
  );
};

const AgentRegistrations: React.FC<{ children: ReactNode }> = ({ children }) => {
  useInterrupt({
    agentId: AGENT_NAME,
    render: ({ event, resolve }) => {
      const { action_requests, review_configs } = parseInterruptValue(event.value);
      if (action_requests.length === 0) {
        return <></>;
      }
      const action = action_requests[0];
      const review = review_configs.find((c) => c.action_name === action.name);
      const allowed = review?.allowed_decisions ?? ["approve", "reject"];
      return <InterruptRenderer action={action} allowed={allowed} onResolve={resolve} />;
    },
  });

  useRetailToolRenderers();

  return <>{children}</>;
};

export const AgentProvider: React.FC<{ userId: string; children: ReactNode }> = ({
  userId,
  children,
}) => {
  const { threadId, resetThread } = useThread();

  const properties = useMemo(
    () => ({ config: { configurable: { user_id: userId, thread_id: threadId } } }),
    [userId, threadId],
  );

  const contextValue = useMemo<AgentContextValue>(
    () => ({ agentName: AGENT_NAME, threadId, resetThread }),
    [threadId, resetThread],
  );

  return (
    <CopilotKit
      key={threadId}
      runtimeUrl={COPILOT_RUNTIME_URL}
      agent={AGENT_NAME}
      threadId={threadId}
      properties={properties}
      onError={(errorEvent) => {
        console.error("CopilotKit agent error", errorEvent);
      }}
    >
      <AgentContext.Provider value={contextValue}>
        <AgentRegistrations>{children}</AgentRegistrations>
      </AgentContext.Provider>
    </CopilotKit>
  );
};

export const useAgentContext = (): AgentContextValue => {
  const ctx = useContext(AgentContext);
  if (!ctx) {
    throw new Error("useAgentContext must be used within AgentProvider");
  }
  return ctx;
};
