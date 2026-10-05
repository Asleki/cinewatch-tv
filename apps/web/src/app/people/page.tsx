import PeopleDirectory from "@/components/catalog/PeopleDirectory";
import { getPublicApiBaseUrl } from "@/lib/config/public-env";

type Person = { provider_id: number; name: string; profile_url: string | null; known_for_department: string | null; future_path: string };
type Response = { page: number; total_pages: number; department: string | null; items: Person[] };

export default async function PeoplePage() {
  let initial: Response | null = null;
  try {
    const response = await fetch(new URL("/api/v1/directory/people", getPublicApiBaseUrl()), { cache: "no-store" });
    if (response.ok) initial = await response.json() as Response;
  } catch { /* Audience-facing retry lives in the directory. */ }
  return <PeopleDirectory initial={initial} />;
}
