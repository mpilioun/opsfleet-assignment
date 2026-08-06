import { useEffect, useState } from "react";
import { CopilotChat, CopilotChatInput, CopilotChatView } from "@copilotkit/react-core/v2";
import type {
  CopilotChatView as CopilotChatViewType,
  CopilotChatViewProps,
} from "@copilotkit/react-core/v2";

import { useAgentContext } from "./agent-provider";

const INITIAL_MESSAGE =
  "Hi! Ask me about sales, inventory, or customer behavior, or manage your saved reports.";

const RetailChatView = (props: CopilotChatViewProps) => {
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const id = setTimeout(() => setReady(true), 50);
    return () => clearTimeout(id);
  }, []);

  const isEmpty = ready && !props.messages?.length && !props.isConnecting && !props.isRunning;

  return (
    <div className="chat-view-wrapper">
      {isEmpty && (
        <div className="chat-empty-state">
          <p className="chat-empty-title">Retail Insights Agent</p>
          <p className="chat-empty-subtitle">{INITIAL_MESSAGE}</p>
        </div>
      )}
      <CopilotChatView {...props} />
    </div>
  );
};

export const Chat = () => {
  const { agentName, threadId, resetThread } = useAgentContext();

  return (
    <div className="chat-panel">
      <header className="chat-header">
        <div>
          <h1>Chat</h1>
          <p className="chat-header-subtitle">Ask about sales, inventory, and customers</p>
        </div>
        <button type="button" className="btn btn-secondary" onClick={() => resetThread()}>
          New Chat
        </button>
      </header>

      <div className="chat-body">
        <CopilotChat
          key={threadId}
          agentId={agentName}
          threadId={threadId}
          labels={{ welcomeMessageText: INITIAL_MESSAGE }}
          chatView={RetailChatView as typeof CopilotChatViewType}
          input={CopilotChatInput}
          className="chat-surface"
        />
      </div>
    </div>
  );
};
