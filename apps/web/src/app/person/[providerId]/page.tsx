import { notFound } from "next/navigation";

import PersonDetails from "@/components/catalog/PersonDetails";
import LiveDataFailure from "@/components/site/LiveDataFailure";
import { loadCatalogPerson } from "@/lib/api/catalog-client";

export default async function PersonPage({ params }: { params: Promise<{ providerId: string }> }) {
  const { providerId } = await params;
  if (!/^\d+$/.test(providerId)) notFound();
  const person = await loadCatalogPerson(providerId);
  if (!person) return <LiveDataFailure title="Person details are unavailable" message="CineWatch could not load this person right now." />;
  return <PersonDetails person={person} />;
}
