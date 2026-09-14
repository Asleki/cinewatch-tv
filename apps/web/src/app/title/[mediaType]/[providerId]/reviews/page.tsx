import { notFound } from "next/navigation";

import ReviewsPage from "@/components/catalog/ReviewsPage";
import { loadCatalogReviews } from "@/lib/api/catalog-client";

export default async function TitleReviewsPage({ params, searchParams }: { params: Promise<{ mediaType: string; providerId: string }>; searchParams: Promise<{ page?: string }> }) {
  const { mediaType, providerId } = await params;
  const query = await searchParams;
  const page = /^\d+$/.test(query.page ?? "") ? Math.max(1, Number(query.page)) : 1;
  const payload = await loadCatalogReviews(mediaType, providerId, page);
  if (!payload) notFound();
  return <ReviewsPage payload={payload} titlePath={`/title/${mediaType}/${providerId}`} />;
}
