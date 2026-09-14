import { notFound } from "next/navigation";

import CatalogBrowse from "@/components/catalog/CatalogBrowse";
import { loadCatalogBrowse } from "@/lib/api/catalog-client";

export default async function BrowsePage({ params, searchParams }: { params: Promise<{ slug: string }>; searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  const resolved = await params;
  const query = await searchParams;
  const slug = resolved.slug;
  const payload = await loadCatalogBrowse("genre", slug, query);
  if (!payload) notFound();
  return <CatalogBrowse payload={payload} basePath={`/genre/${slug}`} />;
}
