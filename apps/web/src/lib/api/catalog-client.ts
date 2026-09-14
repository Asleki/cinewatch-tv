import type {
  CatalogBrowseResponse,
  CatalogPersonResponse,
  CatalogReviewsResponse,
  CatalogTitleResponse,
} from "@cinewatch/contracts";

import { getPublicApiBaseUrl } from "@/lib/config/public-env";

async function readJson<T>(path: string): Promise<T | null> {
  try {
    const response = await fetch(new URL(path, getPublicApiBaseUrl()), {
      cache: "no-store",
      headers: { Accept: "application/json" },
    });
    if (!response.ok) return null;
    return await response.json() as T;
  } catch {
    return null;
  }
}

export function loadCatalogTitle(mediaType: string, providerId: string) {
  if ((mediaType !== "movie" && mediaType !== "tv") || !/^\d+$/.test(providerId)) {
    return Promise.resolve(null);
  }
  return readJson<CatalogTitleResponse>(`/api/v1/catalog/title/${mediaType}/${providerId}`);
}

export function loadCatalogPerson(providerId: string) {
  if (!/^\d+$/.test(providerId)) return Promise.resolve(null);
  return readJson<CatalogPersonResponse>(`/api/v1/catalog/person/${providerId}`);
}

export function loadCatalogReviews(mediaType: string, providerId: string, page = 1) {
  if ((mediaType !== "movie" && mediaType !== "tv") || !/^\d+$/.test(providerId)) {
    return Promise.resolve(null);
  }
  return readJson<CatalogReviewsResponse>(`/api/v1/catalog/title/${mediaType}/${providerId}/reviews?page=${page}`);
}

export function loadCatalogBrowse(
  kind: "genre" | "collection" | "country",
  slug: string,
  query: Record<string, string | string[] | undefined>,
) {
  const params = new URLSearchParams();
  for (const key of ["page", "media_type", "year", "language", "sort"]) {
    const value = query[key];
    if (typeof value === "string" && value) params.set(key, value);
  }
  const suffix = params.size ? `?${params.toString()}` : "";
  return readJson<CatalogBrowseResponse>(`/api/v1/catalog/browse/${kind}/${encodeURIComponent(slug)}${suffix}`);
}
