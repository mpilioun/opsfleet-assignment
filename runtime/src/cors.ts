import cors from "cors";
import type { RequestHandler } from "express";

import { CORS_ALLOWED_ORIGINS } from "./env.js";

function normalizeOrigin(origin: string): string {
  return origin.trim().replace(/\/$/, "");
}

export function createCorsMiddleware(): RequestHandler {
  return cors({
    origin(origin, callback) {
      if (!origin) {
        callback(null, true);
        return;
      }

      const normalizedOrigin = normalizeOrigin(origin);
      const isAllowed = CORS_ALLOWED_ORIGINS.some(
        (allowed) => normalizeOrigin(allowed) === normalizedOrigin,
      );

      if (isAllowed) {
        callback(null, true);
        return;
      }

      callback(new Error("Not allowed by CORS"));
    },
    credentials: true,
    allowedHeaders: ["Content-Type"],
  });
}
