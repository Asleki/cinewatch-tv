import { notFound } from "next/navigation";

import TitleDetails from "@/components/catalog/TitleDetails";
import LiveDataFailure from "@/components/site/LiveDataFailure";
import { loadCatalogTitle } from "@/lib/api/catalog-client";

export default async function TitleFullDetailsPage({ params }: { params: Promise<{ mediaType: string; providerId: string }> }) {
  const { mediaType, providerId } = await params;
  if ((mediaType !== "movie" && mediaType !== "tv") || !/^\d+$/.test(providerId)) notFound();
  const title = await loadCatalogTitle(mediaType, providerId);
  if (!title) return <LiveDataFailure title="Full title details are unavailable" message="CineWatch could not load the full details for this title right now." />;
  return <TitleDetails title={title} fullView />;
}
