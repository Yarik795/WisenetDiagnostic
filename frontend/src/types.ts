export type CheckStatus =
  | "online"
  | "offline"
  | "unknown"
  | "disabled"
  | "checking";

export interface Recorder {
  id: string;
  object_name: string;
  name: string | null;
  host: string;
  port: number;
  use_https: boolean;
  enabled: boolean;
  last_status: CheckStatus | null;
  last_check_at: string | null;
  last_error: string | null;
}

export interface RecorderCreate {
  object_name: string;
  name?: string | null;
  host: string;
  port: number;
  use_https: boolean;
  enabled: boolean;
}

export interface Credentials {
  username: string;
  password: string;
}

export interface CheckResult {
  status: CheckStatus;
  checked_at: string;
  error: string | null;
  model: string | null;
  firmware_version: string | null;
  device_type: string | null;
}

export interface RecorderCheckResponse {
  recorder: Recorder;
  check: CheckResult;
}

export interface ObjectGroup {
  objectName: string;
  recorders: Recorder[];
  aggregateStatus: CheckStatus;
}
