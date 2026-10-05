import OrganizationRoute from "@/components/catalog/OrganizationRoute";
export default async function NetworkPage({ params }: { params: Promise<{ providerId: string }> }) {
  return <OrganizationRoute kind="network" providerId={(await params).providerId} />;
}
