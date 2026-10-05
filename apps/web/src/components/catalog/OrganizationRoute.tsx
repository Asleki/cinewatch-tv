import { notFound } from "next/navigation";
import { OrganizationPage, type OrganizationDetail } from "./OrganizationDirectory";
import { getPublicApiBaseUrl } from "@/lib/config/public-env";

export default async function OrganizationRoute({ kind, providerId }: { kind: "network" | "company"; providerId: string }) {
  if (!/^\d+$/.test(providerId)) notFound();
  let detail: OrganizationDetail | null = null;
  let missing = false;
  try {
    const response = await fetch(new URL(`/api/v1/directory/${kind}/${providerId}`, getPublicApiBaseUrl()), { cache: "no-store" });
    missing = response.status === 404;
    if (response.ok) detail = await response.json() as OrganizationDetail;
  } catch { /* Display the service state. */ }
  if (missing) notFound();
  return detail ? <OrganizationPage detail={detail} /> : <main style={{padding:32}}>Organization details are temporarily unavailable.</main>;
}
