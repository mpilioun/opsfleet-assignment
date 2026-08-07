import { useChartRenderer } from "./chart-renderer";
import { useDataRenderers } from "./data-renderers";
import { useGoldenBucketRenderers } from "./golden-renderers";
import { useReportRenderers } from "./report-renderers";
import { useSubagentRenderers } from "./subagent-renderers";

/** One registration point for every backend tool's chat card. A tool with no
 *  renderer here still works - CopilotKit falls back to its default rendering. */
export const useRetailToolRenderers = (): void => {
  useSubagentRenderers();
  useDataRenderers();
  useGoldenBucketRenderers();
  useReportRenderers();
  useChartRenderer();
};
