import { useRenderTool } from "@copilotkit/react-core/v2";
import { z } from "zod";

import { AGENT_BACKEND_URL } from "../../config";
import { isErrorResult, MutedText } from "./tool-display";
import { ToolCard } from "./tool-card";

const chartSchema = z.object({
  title: z.string().optional(),
  chart_type: z.enum(["bar", "line"]).optional(),
  labels: z.array(z.string()).optional(),
  values: z.array(z.number()).optional(),
});

function extractChartUrl(result: string | undefined): string | null {
  if (!result) return null;
  const match = result.match(/Chart saved to (\S+)/);
  if (!match) return null;
  const path = match[1].replace(/^\.?\/*/, "");
  return `${AGENT_BACKEND_URL}/${path}`;
}

export const useChartRenderer = (): void => {
  useRenderTool(
    {
      name: "generate_chart",
      parameters: chartSchema,
      render: ({ status, parameters, result }) => {
        const errored = status === "complete" && isErrorResult(result);
        const chartUrl = status === "complete" && !errored ? extractChartUrl(result) : null;

        return (
          <ToolCard.Root tone="info" status={status} variant={errored ? "error" : "default"}>
            <ToolCard.Header title={parameters?.title ?? "Chart"}>
              <ToolCard.Subtitle>
                <MutedText>
                  {status !== "complete"
                    ? "Generating chart…"
                    : errored
                      ? result
                      : "Chart generated"}
                </MutedText>
              </ToolCard.Subtitle>
            </ToolCard.Header>
            {chartUrl && (
              <ToolCard.Body>
                <img
                  src={chartUrl}
                  alt={parameters?.title ?? "Generated chart"}
                  className="chart-image"
                />
              </ToolCard.Body>
            )}
          </ToolCard.Root>
        );
      },
    },
    [],
  );
};
