import { notFound } from "next/navigation";

import TitleDetails from "@/components/catalog/TitleDetails";
import { loadCatalogTitle } from "@/lib/api/catalog-client";

export default async function TitlePage({ params, searchParams }: { params: Promise<{ mediaType: string; providerId: string }>; searchParams: Promise<{ view?: string }> }) {
  const { mediaType, providerId } = await params;
  const query = await searchParams;
  const title = await loadCatalogTitle(mediaType, providerId);
  if (!title) notFound();
  return <TitleDetails title={title} fullView={query.view === "full"} />;
}
