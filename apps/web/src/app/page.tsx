import type { HomeResponse } from "@cinewatch/contracts";

import HomepageExperience from "@/components/home/HomepageExperience";
import { getPublicApiBaseUrl } from "@/lib/config/public-env";

async function loadHome(): Promise<HomeResponse | null> {
  try {
    const response = await fetch(new URL("/api/v1/home", getPublicApiBaseUrl()), {
      cache: "no-store",
      headers: { Accept: "application/json" },
    });
    if (!response.ok) return null;
    return await response.json() as HomeResponse;
  } catch {
    return null;
  }
}

export default async function HomePage() {
  const home = await loadHome();
  return <HomepageExperience initialHome={home} />;
}
