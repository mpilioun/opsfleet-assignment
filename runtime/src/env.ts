import { config as loadEnv } from "dotenv";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";

const srcDir = fileURLToPath(new URL(".", import.meta.url));
const projectRoot = resolve(srcDir, "..");

loadEnv({ path: resolve(projectRoot, ".env") });

export const COPILOTKIT_BASE_PATH = "/api/copilotkit/retail-insights-agent";

export const COPILOTKIT_SERVER_PORT = Number.parseInt(
  process.env.COPILOTKIT_SERVER_PORT ?? "3001",
  10,
);

export const AGENT_NAME = process.env.AGENT_NAME ?? "retail-insights-agent";

// Where the FastAPI/AG-UI backend (src/app/main.py) is listening.
export const AGENT_BACKEND_URL =
  process.env.AGENT_BACKEND_URL ?? "http://127.0.0.1:8000";

function normalizeOrigin(origin: string): string {
  return origin.trim().replace(/\/$/, "");
}

export const CORS_ALLOWED_ORIGINS = (
  process.env.CORS_ALLOWED_ORIGINS ?? "http://localhost:5173"
)
  .split(",")
  .map(normalizeOrigin)
  .filter(Boolean);
