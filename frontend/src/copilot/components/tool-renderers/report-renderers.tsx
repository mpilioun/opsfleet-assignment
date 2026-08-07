import { useRenderTool } from "@copilotkit/react-core/v2";
import { z } from "zod";

import { ToolCard } from "../tool-card";
import { isErrorResult, KVRow, MutedText } from "../tool-display";
import { TOOL_NAMES } from "./constants";

const saveSchema = z.object({
  title: z.string().optional(),
});

const findSchema = z.object({
  query: z.string().optional(),
  this_conversation_only: z.boolean().optional(),
});

const deleteSchema = z.object({
  report_ids: z.array(z.string()).optional(),
});

const verifySchema = z.object({
  question: z.string().optional(),
});

export const useReportRenderers = (): void => {
  useRenderTool(
    {
      name: TOOL_NAMES.SAVE_REPORT,
      parameters: saveSchema,
      render: ({ status, parameters, result }) => {
        const errored = status === "complete" && isErrorResult(result);
        return (
          <ToolCard.Root tone="info" status={status} variant={errored ? "error" : "default"}>
            <ToolCard.Header title="Save report">
              <ToolCard.Subtitle>
                <MutedText>
                  {status !== "complete"
                    ? "Saving to your reports library…"
                    : errored
                      ? result
                      : "Saved to your reports library"}
                </MutedText>
              </ToolCard.Subtitle>
            </ToolCard.Header>
            {parameters?.title && (
              <ToolCard.Body>
                <KVRow label="Title">{parameters.title}</KVRow>
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
      name: TOOL_NAMES.FIND_REPORTS,
      parameters: findSchema,
      render: ({ status, parameters, result }) => {
        const errored = status === "complete" && isErrorResult(result);
        const scope = parameters?.this_conversation_only ? "this conversation" : "all reports";
        return (
          <ToolCard.Root status={status} variant={errored ? "error" : "default"}>
            <ToolCard.Header title="Find reports">
              <ToolCard.Subtitle>
                <MutedText>
                  {status !== "complete" ? `Searching ${scope}…` : `Searched ${scope}`}
                </MutedText>
              </ToolCard.Subtitle>
            </ToolCard.Header>
            {parameters?.query && (
              <ToolCard.Body>
                <KVRow label="Query">{parameters.query}</KVRow>
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
      name: TOOL_NAMES.DELETE_REPORTS,
      parameters: deleteSchema,
      render: ({ status, parameters, result }) => {
        const errored = status === "complete" && isErrorResult(result);
        const count = parameters?.report_ids?.length ?? 0;
        // Destructive tone even on success: the approval card already ran, this card
        // is the receipt for what was actually deleted.
        return (
          <ToolCard.Root tone="destructive" status={status} variant={errored ? "error" : "default"}>
            <ToolCard.Header title="Delete reports">
              <ToolCard.Subtitle>
                <MutedText>
                  {status !== "complete"
                    ? `Deleting ${count} report(s)…`
                    : (result ?? `Deleted ${count} report(s)`)}
                </MutedText>
              </ToolCard.Subtitle>
            </ToolCard.Header>
          </ToolCard.Root>
        );
      },
    },
    [],
  );

  useRenderTool(
    {
      name: TOOL_NAMES.VERIFY_OUTPUT,
      parameters: verifySchema,
      render: ({ status, result }) => {
        const errored = status === "complete" && isErrorResult(result);
        return (
          <ToolCard.Root status={status} variant={errored ? "error" : "default"}>
            <ToolCard.Header title="Self-check report">
              <ToolCard.Subtitle>
                <MutedText>
                  {status !== "complete"
                    ? "Checking the draft answers the question, is grounded, and leaks no PII…"
                    : (result ?? "Verification finished")}
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
