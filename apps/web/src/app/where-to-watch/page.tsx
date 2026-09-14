import Link from "next/link";

import styles from "@/app/r3-page.module.css";
import { MediaTypeIcon } from "@/components/catalog/MediaIdentity";
import { getPublicApiBaseUrl } from "@/lib/config/public-env";

type Source = { source_id: number | null; name: string; source_type: string | null; region: string | null; web_url: string | null; format: string | null; price: number | null };
type Payload = { media_type: "movie" | "tv"; tmdb_id: number; region: string; sources: Source[] };

async function load(mediaType: string, tmdbId: string, region: string): Promise<Payload | null> {
  if ((mediaType !== "movie" && mediaType !== "tv") || !/^\d+$/.test(tmdbId)) return null;
  try {
    const url = new URL("/api/v1/external/where-to-watch", getPublicApiBaseUrl());
    url.searchParams.set("media_type", mediaType);
    url.searchParams.set("tmdb_id", tmdbId);
    url.searchParams.set("region", region);
    const response = await fetch(url, { cache: "no-store", headers: { Accept: "application/json" } });
    if (!response.ok) return null;
    return await response.json() as Payload;
  } catch {
    return null;
  }
}

export default async function WhereToWatchPage({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  const query = await searchParams;
  const mediaType = typeof query.media_type === "string" ? query.media_type : "";
  const tmdbId = typeof query.tmdb_id === "string" ? query.tmdb_id : "";
  const title = typeof query.title === "string" ? query.title.trim().slice(0, 260) : "";
  const region = typeof query.region === "string" && query.region.trim() ? query.region.trim().toUpperCase().slice(0, 8) : "US";
  const hasIdentity = (mediaType === "movie" || mediaType === "tv") && /^\d+$/.test(tmdbId);
  const payload = hasIdentity ? await load(mediaType, tmdbId, region) : null;

  return <main className={styles.page}>
    <section className={styles.hero}>
      <p className={styles.eyebrow}>Available Elsewhere</p>
      <h1>{title || "Where to Watch"}</h1>
      <p>See external availability without leaving the distinction between other services and CineWatch Stream Now.</p>
      {hasIdentity ? <div className={styles.identityLine}><MediaTypeIcon mediaType={mediaType as "movie" | "tv"} withLabel /><span>{region}</span></div> : null}
    </section>

    {!hasIdentity ? (
      <section className={styles.section}>
        <div className={styles.emptyPanel}>
          <h2>Choose a title first</h2>
          <p>Open any movie or TV title and choose <strong>Where to Watch</strong> to check its external availability.</p>
          <Link className={styles.button} href="/discover/trending">Browse CineWatch</Link>
        </div>
      </section>
    ) : !payload ? (
      <section className={styles.section}><div className={styles.error}><strong>Availability could not be loaded.</strong></div></section>
    ) : payload.sources.length === 0 ? (
      <section className={styles.section}><p className={styles.muted}>No external availability was found for {payload.region}.</p></section>
    ) : (
      <section className={styles.section}>
        <div className={styles.sectionHead}><h2>Available in {payload.region}</h2></div>
        <div className={styles.grid}>{payload.sources.map((source, index) => {
          const content = <div className={styles.cardBody}><small>{source.source_type || "Availability"}</small><strong>{source.name}</strong><p>{[source.format, source.price != null ? `$${source.price}` : null].filter(Boolean).join(" · ")}</p></div>;
          return source.web_url ? <a key={`${source.source_id ?? source.name}-${index}`} className={styles.card} href={source.web_url} target="_blank" rel="noopener noreferrer">{content}</a> : <div key={`${source.source_id ?? source.name}-${index}`} className={styles.card}>{content}</div>;
        })}</div>
      </section>
    )}
  </main>;
}
