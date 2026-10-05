import { OrganizationDirectory, type Organization } from "@/components/catalog/OrganizationDirectory";
import { getPublicApiBaseUrl } from "@/lib/config/public-env";

export default async function NetworksPage() {
  let initial: { page: number; has_more: boolean; items: Organization[] } | null = null;
  try {
    const response = await fetch(new URL("/api/v1/directory/organizations", getPublicApiBaseUrl()), { cache: "no-store" });
    if (response.ok) initial = await response.json() as { page: number; has_more: boolean; items: Organization[] };
  } catch { /* Display the service state. */ }
  return <OrganizationDirectory initial={initial} />;
}
