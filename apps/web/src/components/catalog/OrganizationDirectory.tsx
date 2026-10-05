"use client";
/* eslint-disable @next/next/no-img-element */
import Link from "next/link";
import { useState } from "react";
import styles from "./OrganizationDirectory.module.css";

export type Organization = { provider_id: number; kind: "network" | "company"; name: string; logo_url: string | null; origin_country: string | null; headquarters: string | null; homepage_url: string | null; future_path: string };
export type OrganizationDetail = { organization: Organization; description: string | null; backdrop_url: string | null; backdrop_media_type: "movie" | "tv" | null; backdrop_title_id: number | null; movie_count: number | null; series_count: number | null };

export function OrganizationDirectory({ initial }: { initial: { page: number; has_more: boolean; items: Organization[] } | null }) {
  const [items, setItems] = useState(initial?.items ?? []);
  const [page, setPage] = useState(initial?.page ?? 0);
  const [hasMore, setHasMore] = useState(initial?.has_more ?? false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(false);
  async function load() {
    setBusy(true);setError(false);
    try {
      const response = await fetch(`/api/cinewatch/directory/organizations?page=${page + 1}`, { cache: "no-store" });
      if (!response.ok) throw new Error("Organizations unavailable");
      const next = await response.json() as {page:number;has_more:boolean;items:Organization[]};
      setItems((current) => [...current, ...next.items.filter((item) => !current.some((old) => old.kind === item.kind && old.provider_id === item.provider_id))]);
      setPage(next.page);setHasMore(next.has_more);
    } catch { setError(true); }
    finally { setBusy(false); }
  }
  return <main className={styles.page}><p className={styles.eyebrow}>Discover</p><h1>Networks & Companies</h1><p className={styles.intro}>Explore the networks and production companies connected to CineWatch titles.</p>
    {items.length ? <div className={styles.grid}>{items.map((item) => <article className={styles.card} key={`${item.kind}-${item.provider_id}`}>
      <Link href={item.future_path} className={styles.logo} aria-label={`Explore ${item.name}`}>{item.logo_url ? <img src={item.logo_url} alt={`${item.name} logo`} /> : <span className={styles.fallback}>C</span>}</Link>
      <Link href={item.future_path} className={styles.name}>{item.name}</Link>
      <small>{item.kind === "network" ? "TV network" : "Production company"}</small>
      {item.headquarters || item.origin_country ? <p>{item.headquarters || item.origin_country}</p> : null}
      {item.homepage_url ? <a className={styles.external} href={item.homepage_url} target="_blank" rel="noopener noreferrer">Official website ↗</a> : null}
    </article>)}</div> : <p>Organizations are temporarily unavailable.</p>}
    {error ? <p className={styles.intro}>More organizations could not be loaded. <button type="button" onClick={() => void load()}>Retry</button></p> : null}
    {hasMore ? <div className={styles.more}><button type="button" disabled={busy} onClick={() => void load()}>{busy ? "Loading…" : "Load more"}</button></div> : null}
  </main>;
}

export function OrganizationPage({ detail }: { detail: OrganizationDetail }) {
  const { organization: org } = detail;
  return <main className={styles.page}>
    <section className={styles.hero} style={detail.backdrop_url ? { backgroundImage: `linear-gradient(90deg,var(--cw-bg) 4%,transparent 130%),url(${detail.backdrop_url})` } : undefined}>
      <div className={styles.heroText}><p className={styles.eyebrow}>{org.kind === "network" ? "TV network" : "Production company"}</p><h1>{org.name}</h1>
        <Link className={styles.info} href="#about">More Info</Link></div>
      <div className={styles.heroSide}><div className={styles.heroLogo}>{org.logo_url ? <img src={org.logo_url} alt={`${org.name} logo`} /> : <span className={styles.fallback}>C</span>}</div>
        {detail.movie_count !== null ? <strong>{detail.movie_count.toLocaleString()} movies</strong> : null}
        {detail.series_count !== null ? <strong>{detail.series_count.toLocaleString()} series</strong> : null}</div>
    </section>
    <section id="about" className={styles.about}><h2>About {org.name}</h2>
      {detail.description ? <p>{detail.description}</p> : null}
      {org.headquarters ? <p><b>Headquarters</b> {org.headquarters}</p> : null}
      {org.origin_country ? <p><b>Country of origin</b> {org.origin_country}</p> : null}
      {org.homepage_url ? <a className={styles.external} href={org.homepage_url} target="_blank" rel="noopener noreferrer">Official website ↗</a> : null}
      {!detail.description && !org.headquarters && !org.origin_country ? <p>More organization information is not available in this catalog.</p> : null}
    </section>
  </main>;
}
