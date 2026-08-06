export interface ActionRequest {
  name: string;
  args: Record<string, unknown>;
}

export interface ReviewConfig {
  action_name: string;
  allowed_decisions: string[];
}

export interface InterruptValue {
  action_requests: ActionRequest[];
  review_configs: ReviewConfig[];
}

export const EMPTY_INTERRUPT: InterruptValue = {
  action_requests: [],
  review_configs: [],
};

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === "object" && value !== null && !Array.isArray(value);

const toActionRequest = (value: unknown): ActionRequest | null => {
  if (!isRecord(value)) return null;
  const name = value.name;
  if (typeof name !== "string") return null;
  const rawArgs = value.args;
  return { name, args: isRecord(rawArgs) ? rawArgs : {} };
};

const toReviewConfig = (value: unknown): ReviewConfig | null => {
  if (!isRecord(value)) return null;
  const actionName = value.action_name;
  if (typeof actionName !== "string") return null;
  const rawAllowed = value.allowed_decisions;
  const allowed = Array.isArray(rawAllowed)
    ? rawAllowed.filter((d): d is string => typeof d === "string")
    : [];
  return { action_name: actionName, allowed_decisions: allowed };
};

const normalize = (value: unknown): InterruptValue => {
  if (!isRecord(value)) return EMPTY_INTERRUPT;
  return {
    action_requests: Array.isArray(value.action_requests)
      ? value.action_requests.map(toActionRequest).filter((r): r is ActionRequest => r !== null)
      : [],
    review_configs: Array.isArray(value.review_configs)
      ? value.review_configs.map(toReviewConfig).filter((c): c is ReviewConfig => c !== null)
      : [],
  };
};

export const parseInterruptValue = (raw: unknown): InterruptValue => {
  if (raw == null) return EMPTY_INTERRUPT;
  if (typeof raw === "string") {
    try {
      return normalize(JSON.parse(raw) as unknown);
    } catch {
      return EMPTY_INTERRUPT;
    }
  }
  return normalize(raw);
};
