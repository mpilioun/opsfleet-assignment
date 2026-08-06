export const AGENT_NAME = import.meta.env.VITE_AGENT_NAME ?? "retail-insights-agent";

const COPILOT_RUNTIME_BASE_URL =
  import.meta.env.VITE_COPILOT_RUNTIME_URL ?? "http://localhost:3001";

// Must match COPILOTKIT_BASE_PATH in runtime/src/env.ts
export const COPILOT_RUNTIME_URL = `${COPILOT_RUNTIME_BASE_URL}/api/copilotkit/${AGENT_NAME}`;

export const AGENT_BACKEND_URL =
  import.meta.env.VITE_AGENT_BACKEND_URL ?? "http://localhost:8000";
