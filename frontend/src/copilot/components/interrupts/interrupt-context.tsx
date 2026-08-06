import { createContext, useContext, useState, type ReactNode } from "react";

export type DecisionType = "approve" | "reject" | "edit";

export interface Decision {
  type: DecisionType;
  edited_action?: { name: string; args: Record<string, unknown> };
}

export interface ToolAction {
  name: string;
  args: Record<string, unknown>;
}

export interface InterruptState {
  editing: boolean;
  resolved: boolean;
}

export interface InterruptActions {
  approve(): void;
  reject(): void;
  startEdit(): void;
  cancelEdit(): void;
  submitEditWithArgs(args: Record<string, unknown>): void;
}

export interface InterruptMeta {
  action: ToolAction;
  allowed: string[];
}

interface InterruptContextValue {
  state: InterruptState;
  actions: InterruptActions;
  meta: InterruptMeta;
}

const InterruptContext = createContext<InterruptContextValue | null>(null);

export function InterruptProvider({
  state,
  actions,
  meta,
  children,
}: {
  state: InterruptState;
  actions: InterruptActions;
  meta: InterruptMeta;
  children: ReactNode;
}) {
  return (
    <InterruptContext.Provider value={{ state, actions, meta }}>
      {children}
    </InterruptContext.Provider>
  );
}

export function useInterruptState({
  action,
  allowed,
  onResolve,
}: {
  action: ToolAction;
  allowed: string[];
  onResolve: (value: { decisions: Decision[] }) => void;
}): { state: InterruptState; actions: InterruptActions; meta: InterruptMeta } {
  const [editing, setEditing] = useState(false);
  const [resolved, setResolved] = useState(false);

  const state: InterruptState = { editing, resolved };

  const actions: InterruptActions = {
    approve: () => {
      setResolved(true);
      onResolve({ decisions: [{ type: "approve" }] });
    },
    reject: () => {
      setResolved(true);
      onResolve({ decisions: [{ type: "reject" }] });
    },
    startEdit: () => setEditing(true),
    cancelEdit: () => setEditing(false),
    submitEditWithArgs: (args) => {
      setResolved(true);
      onResolve({ decisions: [{ type: "edit", edited_action: { name: action.name, args } }] });
    },
  };

  const meta: InterruptMeta = { action, allowed };

  return { state, actions, meta };
}

export const useInterruptContext = (): InterruptContextValue => {
  const ctx = useContext(InterruptContext);
  if (!ctx) {
    throw new Error("useInterruptContext must be used within InterruptProvider");
  }
  return ctx;
};
