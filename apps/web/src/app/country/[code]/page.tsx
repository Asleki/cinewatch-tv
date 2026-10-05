import { notFound } from "next/navigation";

import CatalogBrowse from "@/components/catalog/CatalogBrowse";
import { loadCatalogBrowse } from "@/lib/api/catalog-client";
import { getPublicApiBaseUrl } from "@/lib/config/public-env";
import type { HomeGenresResponse } from "@cinewatch/contracts";

async function loadGenreOptions() {
  try {
    const response = await fetch(new URL("/api/v1/home/genres", getPublicApiBaseUrl()), { cache: "no-store" });
    if (!response.ok) return [];
    const payload = await response.json() as HomeGenresResponse;
    return (payload.genres ?? []).map(({ slug, name }) => ({ slug, name }));
  } catch { return []; }
}

export default async function BrowsePage({ params, searchParams }: { params: Promise<{ code: string }>; searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  const resolved = await params;
  const query = await searchParams;
  const slug = resolved.code;
  const [payload, genreOptions] = await Promise.all([loadCatalogBrowse("country", slug, query), loadGenreOptions()]);
  if (!payload) notFound();
  return <CatalogBrowse payload={payload} basePath={`/country/${slug}`} genreOptions={genreOptions} />;
}
