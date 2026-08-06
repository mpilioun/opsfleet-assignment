import express from "express";
import {
  CopilotRuntime,
  ExperimentalEmptyAdapter,
  copilotRuntimeNodeExpressEndpoint,
} from "@copilotkit/runtime";
import { LangGraphHttpAgent } from "@copilotkit/runtime/langgraph";

import { createCorsMiddleware } from "./cors.js";
import {
  AGENT_BACKEND_URL,
  AGENT_NAME,
  COPILOTKIT_BASE_PATH,
  COPILOTKIT_SERVER_PORT,
  CORS_ALLOWED_ORIGINS,
} from "./env.js";

// A dropped connection to the backend (e.g. it hot-reloads mid-stream) throws
// an unhandled error deep inside undici's fetch, which would otherwise crash
// this whole process instead of just failing that one request. Log and stay up.
process.on("uncaughtException", (err) => {
  console.error("Uncaught exception (backend connection likely dropped) - continuing", err);
});
process.on("unhandledRejection", (reason) => {
  console.error("Unhandled rejection (backend connection likely dropped) - continuing", reason);
});

const serviceAdapter = new ExperimentalEmptyAdapter();
const agentUrl = `${AGENT_BACKEND_URL}/${AGENT_NAME}`;

const runtime = new CopilotRuntime({
  agents: {
    [AGENT_NAME]: new LangGraphHttpAgent({ url: agentUrl }),
  },
});

const app = express();

app.get("/health", (_req, res) => {
  res.status(200).json({ status: "ok" });
});

app.use(createCorsMiddleware());

// Mounted at root, not at COPILOTKIT_BASE_PATH: the handler's own internal
// router does its own basePath-based matching against the full request path
// (via options.endpoint) - mounting it with a path here would make Express
// strip that prefix first, so the handler's router would never match.
app.use(
  copilotRuntimeNodeExpressEndpoint({
    endpoint: COPILOTKIT_BASE_PATH,
    runtime,
    serviceAdapter,
  }),
);

app.listen(COPILOTKIT_SERVER_PORT, "0.0.0.0", () => {
  console.log("CopilotKit runtime listening", {
    port: COPILOTKIT_SERVER_PORT,
    basePath: COPILOTKIT_BASE_PATH,
    agentName: AGENT_NAME,
    agentUrl,
    corsOrigins: CORS_ALLOWED_ORIGINS,
  });
});
