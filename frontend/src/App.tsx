import { useState } from "react";
import { AgentProvider } from "./copilot/agent-provider";
import { Chat } from "./copilot/chat";

const STORAGE_KEY = "retail-insights-user-id";

function ManagerIdGate({ onSubmit }: { onSubmit: (userId: string) => void }) {
  const [value, setValue] = useState("");

  return (
    <div className="gate">
      <form
        className="gate-form"
        onSubmit={(e) => {
          e.preventDefault();
          const trimmed = value.trim();
          if (trimmed) onSubmit(trimmed);
        }}
      >
        <h1>Retail Insights Agent</h1>
        <p>Enter a manager ID to start (no auth in this prototype).</p>
        <input
          autoFocus
          value={value}
          onChange={(e) => setValue(e.target.value)}
          placeholder="e.g. manager-1"
        />
        <button type="submit" className="btn btn-approve">
          Continue
        </button>
      </form>
    </div>
  );
}

export default function App() {
  const [userId, setUserId] = useState<string | null>(() => localStorage.getItem(STORAGE_KEY));

  if (!userId) {
    return (
      <ManagerIdGate
        onSubmit={(id) => {
          localStorage.setItem(STORAGE_KEY, id);
          setUserId(id);
        }}
      />
    );
  }

  return (
    <div className="app-shell">
      <AgentProvider userId={userId}>
        <Chat />
      </AgentProvider>
    </div>
  );
}
