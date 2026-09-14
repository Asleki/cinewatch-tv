/* eslint-disable @next/next/no-img-element */

import Link from "next/link";
import { notFound } from "next/navigation";

import styles from "@/app/r3-page.module.css";
import LiveDataFailure from "@/components/site/LiveDataFailure";
import { getPublicApiBaseUrl } from "@/lib/config/public-env";

type Summary = { provider_id: number; media_type: "movie" | "tv"; title: string; year: number | null; poster_url: string | null; future_path: string };
type ProviderResponse = { provider_id: number; name: string; logo_url: string | null; region: string; official_homepage_url: string | null; items: Summary[] };

async function loadProvider(providerId: string): Promise<ProviderResponse | null> {
  try {
    const response = await fetch(new URL(`/api/v1/catalog/provider/${providerId}?region=US`, getPublicApiBaseUrl()), { cache: "no-store", headers: { Accept: "application/json" } });
    if (!response.ok) return null;
    return await response.json() as ProviderResponse;
  } catch { return null; }
}

export default async function ProviderPage({ params }: { params: Promise<{ providerId: string }> }) {
  const { providerId } = await params;
  if (!/^\d+$/.test(providerId)) notFound();
  const provider = await loadProvider(providerId);
  if (!provider) return <LiveDataFailure title="Streaming service unavailable" message="CineWatch could not load this streaming service right now." />;
  return (
    <main className={styles.page}>
      <section className={styles.hero}>
        <div className={styles.providerHero}>
          {provider.logo_url ? <img src={provider.logo_url} alt={`${provider.name} logo`} /> : <div />}
          <div><p className={styles.eyebrow}>Streaming service · {provider.region}</p><h1>{provider.name}</h1><p>Explore titles associated with this service.</p></div>
        </div>
        {provider.official_homepage_url ? <div className={styles.actions}><a className={styles.button} href={provider.official_homepage_url} target="_blank" rel="noopener noreferrer">Open official website ↗</a></div> : <p className={styles.muted}>No official website is available here yet.</p>}
      </section>
      <section className={styles.section}>
        <div className={styles.sectionHead}><div><p className={styles.eyebrow}>Discover</p><h2>Available titles</h2></div></div>
        {provider.items.length ? <div className={styles.posterGrid}>{provider.items.map((item) => <Link className={styles.posterCard} href={item.future_path} key={`${item.media_type}-${item.provider_id}`}>{item.poster_url ? <img src={item.poster_url} alt="" /> : <span className={styles.posterFallback}>C</span>}<strong>{item.title}</strong><small>{item.year ?? (item.media_type === "movie" ? "Movie" : "TV")}</small></Link>)}</div> : <p className={styles.muted}>No titles are available for this service and region.</p>}
      </section>
    </main>
  );
}
