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

app.use(
  COPILOTKIT_BASE_PATH,
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
