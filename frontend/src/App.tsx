import { useState } from "react";
import { v4 as uuidv4 } from "uuid";
import { AgentProvider } from "./copilot/agent-provider";
import { Chat } from "./copilot/chat";

const STORAGE_KEY = "retail-insights-user-id";

// ponytail: native prompt() once per page load - reload to switch user.
// Cached at module scope so StrictMode's double-invoked initializer asks once.
let askedUserId: string | undefined;

function askUserId(): string {
  if (askedUserId) return askedUserId;
  const last = localStorage.getItem(STORAGE_KEY) ?? "";
  const entered = window.prompt("Demo user ID:", last)?.trim();
  askedUserId = entered || last || uuidv4();
  localStorage.setItem(STORAGE_KEY, askedUserId);
  return askedUserId;
}

export default function App() {
  const [userId] = useState<string>(askUserId);

  return (
    <div className="app-shell">
      <AgentProvider userId={userId}>
        <Chat />
      </AgentProvider>
    </div>
  );
}
