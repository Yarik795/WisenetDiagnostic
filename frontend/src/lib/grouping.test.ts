import { describe, expect, it } from "vitest";
import { groupByObject } from "./grouping";
import type { Recorder } from "../types";

function rec(
  id: string,
  object_name: string,
  host: string,
  last_status: Recorder["last_status"] = null
): Recorder {
  return {
    id,
    object_name,
    name: null,
    host,
    port: 80,
    use_https: false,
    enabled: true,
    last_status,
    last_check_at: null,
    last_error: null,
  };
}

describe("groupByObject", () => {
  const recorders = [
    rec("1", "Объект A", "10.0.0.1", "online"),
    rec("2", "Объект A", "10.0.0.2", "offline"),
    rec("3", "Объект B", "10.0.0.3"),
  ];

  it("groups by object_name", () => {
    const groups = groupByObject(recorders, "", "name");
    expect(groups).toHaveLength(2);
    const a = groups.find((g) => g.objectName === "Объект A");
    expect(a?.recorders).toHaveLength(2);
  });

  it("filters by search", () => {
    const groups = groupByObject(recorders, "10.0.0.3", "name");
    expect(groups).toHaveLength(1);
    expect(groups[0].objectName).toBe("Объект B");
  });

  it("sorts problematic first", () => {
    const groups = groupByObject(recorders, "", "status");
    expect(groups[0].objectName).toBe("Объект A");
    expect(groups[0].aggregateStatus).toBe("offline");
  });
});
