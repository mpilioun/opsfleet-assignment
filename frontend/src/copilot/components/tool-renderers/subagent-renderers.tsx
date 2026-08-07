import { useRenderTool } from "@copilotkit/react-core/v2";
import { z } from "zod";

import { ToolCard } from "../tool-card";
import { isErrorResult, MutedText } from "../tool-display";
import { TOOL_NAMES } from "./constants";

const taskSchema = z.object({
  description: z.string().optional(),
  subagent_type: z.string().optional(),
});

const SUBAGENT_LABELS: Record<string, string> = {
  "data-analyst": "Data analyst",
  "report-writer": "Report writer",
};

export const useSubagentRenderers = (): void => {
  useRenderTool(
    {
      name: TOOL_NAMES.TASK,
      parameters: taskSchema,
      render: ({ status, parameters, result }) => {
        const errored = status === "complete" && isErrorResult(result);
        const subagent = parameters?.subagent_type ?? "";
        // Streaming args arrive incrementally, so subagent_type can still be empty
        // on the first render frames.
        const label = SUBAGENT_LABELS[subagent] ?? (subagent || "Delegating");

        return (
          <ToolCard.Root tone="info" status={status} variant={errored ? "error" : "default"}>
            <ToolCard.Header title={label}>
              <ToolCard.Subtitle>
                <MutedText>
                  {status !== "complete" ? "Working…" : "Finished"}
                </MutedText>
              </ToolCard.Subtitle>
            </ToolCard.Header>
            {parameters?.description && (
              <ToolCard.Body>
                <MutedText>{parameters.description}</MutedText>
              </ToolCard.Body>
            )}
          </ToolCard.Root>
        );
      },
    },
    [],
  );
};
