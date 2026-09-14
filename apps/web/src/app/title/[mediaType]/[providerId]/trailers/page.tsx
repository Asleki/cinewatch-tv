import { notFound } from "next/navigation";

import TitleVideos from "@/components/catalog/TitleVideos";
import LiveDataFailure from "@/components/site/LiveDataFailure";
import { loadCatalogTitle, loadCatalogVideos } from "@/lib/api/catalog-client";

export default async function TitleTrailersPage({ params }: { params: Promise<{ mediaType: string; providerId: string }> }) {
  const { mediaType, providerId } = await params;
  if ((mediaType !== "movie" && mediaType !== "tv") || !/^\d+$/.test(providerId)) notFound();
  const [title, videos] = await Promise.all([loadCatalogTitle(mediaType, providerId), loadCatalogVideos(mediaType, providerId)]);
  if (!title || !videos) return <LiveDataFailure title="Trailers are unavailable" message="CineWatch could not load trailers for this title right now." />;
  return <TitleVideos title={title.title} mediaType={title.media_type} providerId={title.provider_id} videos={videos.videos} />;
}
