import { notFound } from "next/navigation";

import PersonDetails from "@/components/catalog/PersonDetails";
import { loadCatalogPerson } from "@/lib/api/catalog-client";

export default async function PersonPage({ params }: { params: Promise<{ providerId: string }> }) {
  const { providerId } = await params;
  const person = await loadCatalogPerson(providerId);
  if (!person) notFound();
  return <PersonDetails person={person} />;
}
