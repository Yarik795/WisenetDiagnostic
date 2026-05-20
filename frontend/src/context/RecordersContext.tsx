import { createContext, useContext, type ReactNode } from "react";
import { useRecorders } from "../hooks/useRecorders";

type RecordersContextValue = ReturnType<typeof useRecorders>;

const RecordersContext = createContext<RecordersContextValue | null>(null);

export function RecordersProvider({ children }: { children: ReactNode }) {
  const value = useRecorders();
  return (
    <RecordersContext.Provider value={value}>
      {children}
    </RecordersContext.Provider>
  );
}

export function useRecordersContext() {
  const ctx = useContext(RecordersContext);
  if (!ctx) {
    throw new Error("useRecordersContext must be used within RecordersProvider");
  }
  return ctx;
}
