const DEFAULT_API_BASE_URL = "http://127.0.0.1:8000";
const DEFAULT_SITE_URL = "http://127.0.0.1:3000";

function parsePublicHttpUrl(name: string, value: string | undefined, fallback: string): URL {
  const candidate = value?.trim() || fallback;
  const url = new URL(candidate);

  if (url.protocol !== "http:" && url.protocol !== "https:") {
    throw new Error(`${name} must use http or https.`);
  }

  return url;
}

export function getPublicApiBaseUrl(): URL {
  return parsePublicHttpUrl(
    "NEXT_PUBLIC_CINEWATCH_API_BASE_URL",
    process.env.NEXT_PUBLIC_CINEWATCH_API_BASE_URL,
    DEFAULT_API_BASE_URL,
  );
}

export function getPublicSiteUrl(): URL {
  return parsePublicHttpUrl(
    "NEXT_PUBLIC_CINEWATCH_SITE_URL",
    process.env.NEXT_PUBLIC_CINEWATCH_SITE_URL,
    DEFAULT_SITE_URL,
  );
}
