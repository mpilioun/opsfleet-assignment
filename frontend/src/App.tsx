import { useState } from "react";
import { v4 as uuidv4 } from "uuid";
import { AgentProvider } from "./copilot/agent-provider";
import { Chat } from "./copilot/chat";

const STORAGE_KEY = "retail-insights-user-id";

function getOrCreateUserId(): string {
  const existing = localStorage.getItem(STORAGE_KEY);
  if (existing) return existing;
  const generated = uuidv4();
  localStorage.setItem(STORAGE_KEY, generated);
  return generated;
}

export default function App() {
  const [userId] = useState<string>(getOrCreateUserId);

  return (
    <div className="app-shell">
      <AgentProvider userId={userId}>
        <Chat />
      </AgentProvider>
    </div>
  );
}
