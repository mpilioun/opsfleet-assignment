export const TOOL_NAMES = {
  // deepagents subagent delegation
  TASK: "task",

  // Data analyst subagent
  RUN_SQL: "run_sql",
  GET_SCHEMA: "get_schema",
  SEARCH_GOLDEN_BUCKET: "search_golden_bucket",

  // Report writer subagent
  GENERATE_CHART: "generate_chart",
  VERIFY_OUTPUT: "verify_output",

  // Root agent (saved reports library)
  SAVE_REPORT: "save_report",
  FIND_REPORTS: "find_reports",
  READ_REPORT: "read_report",
  DELETE_REPORTS: "delete_reports",
} as const;
