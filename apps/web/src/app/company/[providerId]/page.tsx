import OrganizationRoute from "@/components/catalog/OrganizationRoute";
export default async function CompanyPage({ params }: { params: Promise<{ providerId: string }> }) {
  return <OrganizationRoute kind="company" providerId={(await params).providerId} />;
}
