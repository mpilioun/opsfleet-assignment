import { useCallback, useState } from "react";
import { v4 as uuidv4 } from "uuid";

interface UseThreadResult {
  threadId: string;
  resetThread: () => string;
}

export function useThread(): UseThreadResult {
  const [threadId, setThreadId] = useState(() => uuidv4());

  const resetThread = useCallback(() => {
    const newId = uuidv4();
    setThreadId(newId);
    return newId;
  }, []);

  return { threadId, resetThread };
}
