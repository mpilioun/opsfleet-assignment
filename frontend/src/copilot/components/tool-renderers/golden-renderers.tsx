import { useRenderTool } from "@copilotkit/react-core/v2";
import { z } from "zod";

import { ToolCard } from "../tool-card";
import { KVRow, MutedText } from "../tool-display";
import { TOOL_NAMES } from "./constants";

const goldenSchema = z.object({
  question: z.string().optional(),
});

// Past reports are free text, so the generic error sniff would trip on their
// contents - the tool has exactly one non-result, so match that instead.
const NO_MATCHES = "No similar past analyses";

export const useGoldenBucketRenderers = (): void => {
  useRenderTool(
    {
      name: TOOL_NAMES.SEARCH_GOLDEN_BUCKET,
      parameters: goldenSchema,
      render: ({ status, parameters, result }) => (
        <ToolCard.Root tone="info" status={status}>
          <ToolCard.Header title="Consult past analyses">
            <ToolCard.Subtitle>
              <MutedText>
                {status !== "complete"
                  ? "Searching the golden bucket…"
                  : result?.startsWith(NO_MATCHES)
                    ? "No similar past analysis found"
                    : "Found analyst-approved examples"}
              </MutedText>
            </ToolCard.Subtitle>
          </ToolCard.Header>
          {parameters?.question && (
            <ToolCard.Body>
              <KVRow label="Question">{parameters.question}</KVRow>
            </ToolCard.Body>
          )}
        </ToolCard.Root>
      ),
    },
    [],
  );
};
