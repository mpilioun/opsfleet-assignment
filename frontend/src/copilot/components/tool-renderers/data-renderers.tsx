import { useRenderTool } from "@copilotkit/react-core/v2";
import { z } from "zod";

import { ToolCard } from "../tool-card";
import { isErrorResult, MutedText } from "../tool-display";
import { TOOL_NAMES } from "./constants";

const sqlSchema = z.object({
  sql: z.string().optional(),
});

const schemaSchema = z.object({
  table_name: z.string().optional(),
});

export const useDataRenderers = (): void => {
  useRenderTool(
    {
      name: TOOL_NAMES.RUN_SQL,
      parameters: sqlSchema,
      render: ({ status, parameters, result }) => {
        const errored = status === "complete" && isErrorResult(result);
        return (
          <ToolCard.Root tone="info" status={status} variant={errored ? "error" : "default"}>
            <ToolCard.Header title="Query data">
              <ToolCard.Subtitle>
                <MutedText>
                  {status !== "complete"
                    ? "Running SQL against BigQuery…"
                    : errored
                      ? result
                      : "Query returned results"}
                </MutedText>
              </ToolCard.Subtitle>
            </ToolCard.Header>
            {/* The SQL itself is the point of this card: an executive can't audit a
                number they can't trace back to a query. */}
            {parameters?.sql && (
              <ToolCard.Body>
                <pre className="args-block">{parameters.sql}</pre>
              </ToolCard.Body>
            )}
          </ToolCard.Root>
        );
      },
    },
    [],
  );

  useRenderTool(
    {
      name: TOOL_NAMES.GET_SCHEMA,
      parameters: schemaSchema,
      render: ({ status, parameters, result }) => {
        const errored = status === "complete" && isErrorResult(result);
        const target = parameters?.table_name ?? "the full dataset";
        return (
          <ToolCard.Root status={status} variant={errored ? "error" : "default"}>
            <ToolCard.Header title="Inspect schema">
              <ToolCard.Subtitle>
                <MutedText>
                  {status !== "complete"
                    ? `Reading ${target}…`
                    : errored
                      ? result
                      : `Read ${target}`}
                </MutedText>
              </ToolCard.Subtitle>
            </ToolCard.Header>
          </ToolCard.Root>
        );
      },
    },
    [],
  );
};
