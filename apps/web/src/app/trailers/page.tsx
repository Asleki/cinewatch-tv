/* eslint-disable @next/next/no-img-element */

import Link from "next/link";

import styles from "@/app/r3-page.module.css";
import { getPublicApiBaseUrl } from "@/lib/config/public-env";

type Trailer = {
  provider_id: string;
  youtube_video_id: string;
  title: string;
  thumbnail_url: string | null;
  language: string | null;
  categories: string[];
  published_at: string | null;
  media_type: "movie" | "tv" | null;
  tmdb_id: number | null;
  resource_title: string | null;
};
type Payload = { page: number; total_pages: number; total_results: number; trailers: Trailer[] };

async function load(page: number): Promise<Payload | null> {
  try {
    const url = new URL("/api/v1/external/trailers", getPublicApiBaseUrl());
    url.searchParams.set("page", String(page));
    url.searchParams.set("mode", "latest");
    const response = await fetch(url, { cache: "no-store", headers: { Accept: "application/json" } });
    if (!response.ok) return null;
    return await response.json() as Payload;
  } catch {
    return null;
  }
}

export default async function TrailerLibrary({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  const query = await searchParams;
  const page = typeof query.page === "string" && /^\d+$/.test(query.page) ? Math.max(1, Number(query.page)) : 1;
  const payload = await load(page);
  return <main className={styles.page}>
    <section className={styles.hero}>
      <p className={styles.eyebrow}>Trailers & Teasers</p>
      <h1>Trailer Library</h1>
      <p>Fresh trailers, teasers, clips and featurettes connected to real movie and television identities.</p>
    </section>
    {!payload ? <section className={styles.section}><div className={styles.error}><strong>Trailers could not be loaded.</strong></div></section> : payload.trailers.length === 0 ? <section className={styles.section}><p className={styles.muted}>No trailers are available on this page.</p></section> : <>
      <section className={styles.section}>
        <div className={styles.sectionHead}><h2>Latest</h2><span className={styles.muted}>Page {payload.page}{payload.total_pages ? ` of ${payload.total_pages}` : ""}</span></div>
        <div className={styles.grid}>{payload.trailers.map((item) => {
          const titlePath = item.tmdb_id && item.media_type ? `/title/${item.media_type}/${item.tmdb_id}/trailers` : null;
          const card = <>{item.thumbnail_url ? <img src={item.thumbnail_url} alt="" /> : null}<div className={styles.cardBody}><small>{item.categories.join(" · ") || "Video"}</small><strong>{item.resource_title || item.title}</strong><p>{item.title}</p></div></>;
          return titlePath ? <Link className={styles.card} href={titlePath} key={item.provider_id}>{card}</Link> : <a className={styles.card} href={`https://www.youtube.com/watch?v=${encodeURIComponent(item.youtube_video_id)}`} target="_blank" rel="noopener noreferrer" key={item.provider_id}>{card}</a>;
        })}</div>
      </section>
      <nav className={styles.actions} aria-label="Trailer pages">
        {payload.page > 1 ? <Link className={styles.buttonSecondary} href={`/trailers?page=${payload.page - 1}`}>← Previous</Link> : null}
        {payload.total_pages > payload.page ? <Link className={styles.buttonSecondary} href={`/trailers?page=${payload.page + 1}`}>Next →</Link> : null}
      </nav>
    </>}
  </main>;
}
