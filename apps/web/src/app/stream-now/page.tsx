import type { Metadata } from "next";
import StreamNowExperience from "@/components/stream/StreamNowExperience";
import { resolveAuthorizedPlayback } from "@/lib/playable/authority";

export const metadata: Metadata = { title: "Stream Now" };

export default async function StreamNowPage() {
  // Query strings and discovery IDs cannot select or authorize a media source.
  const manifest = await resolveAuthorizedPlayback(null);
  return <section aria-label="Stream Now"><StreamNowExperience manifest={manifest} /></section>;
}
