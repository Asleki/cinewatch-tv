import { getPublicApiBaseUrl } from "@/lib/config/public-env";

export type CineWatchEnvironment =
  | "local"
  | "development"
  | "private-beta"
  | "staging"
  | "production";

export interface HealthResponse {
  status: "ok";
  service: string;
}

export interface StatusResponse {
  status: "ready";
  service: string;
  application: string;
  environment: CineWatchEnvironment;
  api_version: "v1";
}

async function fetchJson<T>(path: string): Promise<T> {
  const url = new URL(path, getPublicApiBaseUrl());
  const response = await fetch(url, {
    cache: "no-store",
    headers: {
      Accept: "application/json",
    },
  });

  if (!response.ok) {
    throw new Error(`CineWatch API request failed with HTTP ${response.status}.`);
  }

  return (await response.json()) as T;
}

export function getApiHealth(): Promise<HealthResponse> {
  return fetchJson<HealthResponse>("/health");
}

export function getApiStatus(): Promise<StatusResponse> {
  return fetchJson<StatusResponse>("/api/v1/status");
}
