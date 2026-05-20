import { describe, expect, it } from "vitest";
import { aggregateStatus, effectiveStatus } from "./status";
import type { Recorder } from "../types";

function rec(
  enabled: boolean,
  last_status: Recorder["last_status"]
): Recorder {
  return {
    id: "1",
    object_name: "A",
    name: null,
    host: "1.1.1.1",
    port: 80,
    use_https: false,
    enabled,
    last_status,
    last_check_at: null,
    last_error: null,
  };
}

describe("status", () => {
  it("returns disabled when recorder disabled", () => {
    expect(effectiveStatus(rec(false, "online"))).toBe("disabled");
  });

  it("aggregates worst status", () => {
    const statuses = aggregateStatus([
      rec(true, "online"),
      rec(true, "offline"),
    ]);
    expect(statuses).toBe("offline");
  });
});
