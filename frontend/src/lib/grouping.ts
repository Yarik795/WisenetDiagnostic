import type { CheckStatus, ObjectGroup, Recorder } from "../types";
import { aggregateStatus, effectiveStatus } from "./status";

export type SortMode = "name" | "status";

export function groupByObject(
  recorders: Recorder[],
  search: string,
  sort: SortMode
): ObjectGroup[] {
  const q = search.trim().toLowerCase();
  const filtered = q
    ? recorders.filter((r) => {
        const name = (r.name ?? "").toLowerCase();
        return (
          r.object_name.toLowerCase().includes(q) ||
          r.host.toLowerCase().includes(q) ||
          name.includes(q)
        );
      })
    : recorders;

  const map = new Map<string, Recorder[]>();
  for (const r of filtered) {
    const list = map.get(r.object_name) ?? [];
    list.push(r);
    map.set(r.object_name, list);
  }

  const groups: ObjectGroup[] = Array.from(map.entries()).map(
    ([objectName, recs]) => ({
      objectName,
      recorders: recs,
      aggregateStatus: aggregateStatus(recs),
    })
  );

  if (sort === "name") {
    groups.sort((a, b) =>
      a.objectName.localeCompare(b.objectName, "ru")
    );
  } else {
    groups.sort((a, b) => {
      const diff =
        statusSortKey(b.aggregateStatus) - statusSortKey(a.aggregateStatus);
      if (diff !== 0) return diff;
      return a.objectName.localeCompare(b.objectName, "ru");
    });
  }

  return groups;
}

function statusSortKey(s: CheckStatus): number {
  const order: Record<CheckStatus, number> = {
    offline: 4,
    checking: 3,
    unknown: 2,
    online: 1,
    disabled: 0,
  };
  return order[s];
}

export function offlineCount(recorders: Recorder[]): number {
  return recorders.filter((r) => effectiveStatus(r) === "offline").length;
}
