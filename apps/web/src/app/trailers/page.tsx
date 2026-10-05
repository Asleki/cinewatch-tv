/* eslint-disable @next/next/no-img-element */
import Link from "next/link";
import styles from "@/app/r3-page.module.css";
import { getPublicApiBaseUrl } from "@/lib/config/public-env";

type Card = { provider_id: number; media_type: "movie" | "tv"; title: string; release_year: number | null; poster_url: string | null; youtube_key: string; video_name: string; video_type: string; video_language: string | null; future_path: string };
type Payload = { page: number; has_more: boolean; items: Card[] };
type Genres = { genres: { slug: string; name: string }[] };
const keys = ["media_type", "genre", "year", "video_language", "video_type"];

function link(query: Record<string, string | string[] | undefined>, page: number) {
  const params = new URLSearchParams({ page: String(page) });
  for (const key of keys) if (typeof query[key] === "string" && query[key]) params.set(key, query[key]);
  return `/trailers?${params}`;
}
async function load(query: Record<string, string | string[] | undefined>): Promise<Payload | null> {
  try {
    const url = new URL("/api/v1/catalog/trailers", getPublicApiBaseUrl());
    for (const key of ["page", ...keys]) if (typeof query[key] === "string" && query[key]) url.searchParams.set(key, query[key]);
    const response = await fetch(url, { cache: "no-store" });
    return response.ok ? await response.json() as Payload : null;
  } catch { return null; }
}
async function loadGenres(): Promise<Genres | null> {
  try {
    const response = await fetch(new URL("/api/v1/home/genres", getPublicApiBaseUrl()), { next: { revalidate: 3600 } });
    return response.ok ? await response.json() as Genres : null;
  } catch { return null; }
}
export default async function TrailerLibrary({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  const query = await searchParams;
  const [payload, genres] = await Promise.all([load(query), loadGenres()]);
  return <main className={styles.page}>
    <section className={styles.hero}><p className={styles.eyebrow}>Discover</p><h1>Trailers</h1><p>Watch trailers, teasers and more from movies and series.</p></section>
    <form className={styles.form} action="/trailers" method="get" style={{gridTemplateColumns:"repeat(auto-fit,minmax(150px,1fr))"}}>
      <select name="media_type" aria-label="Title type" defaultValue={typeof query.media_type === "string" ? query.media_type : "all"}><option value="all">Movies & TV</option><option value="movie">Movies</option><option value="tv">TV Shows</option></select>
      <select name="genre" aria-label="Genre" defaultValue={typeof query.genre === "string" ? query.genre : ""}><option value="">All genres</option>{genres?.genres.map((genre) => <option key={genre.slug} value={genre.slug}>{genre.name}</option>)}</select>
      <input name="year" inputMode="numeric" pattern="[0-9]{4}" aria-label="Title release year" placeholder="Release year" defaultValue={typeof query.year === "string" ? query.year : ""} />
      <select name="video_language" aria-label="Trailer language" defaultValue={typeof query.video_language === "string" ? query.video_language : ""}><option value="">Any video language</option>{[["en","English"],["es","Spanish"],["fr","French"],["hi","Hindi"],["ko","Korean"],["zh","Chinese"]].map(([code,name]) => <option key={code} value={code}>{name}</option>)}</select>
      <select name="video_type" aria-label="Video type" defaultValue={typeof query.video_type === "string" ? query.video_type : ""}><option value="">All video types</option>{["Trailer","Teaser","Clip","Featurette","Behind the Scenes"].map((value) => <option key={value}>{value}</option>)}</select>
      <button type="submit">Apply filters</button>
    </form>
    {!payload ? <section className={styles.section}><div className={styles.error}>Trailers could not be loaded. Please try again.</div></section> : <>
      <section className={styles.section}><div className={styles.sectionHead}><h2>Explore videos</h2></div>
        {payload.items.length ? <div className={styles.grid}>{payload.items.map((card) => <Link className={styles.card} href={card.future_path} key={`${card.media_type}-${card.provider_id}-${card.youtube_key}`}>
          <img src={`https://i.ytimg.com/vi/${encodeURIComponent(card.youtube_key)}/hqdefault.jpg`} alt="" loading="lazy" />
          <div className={styles.cardBody}><small>{card.video_type}{card.video_language ? ` · ${card.video_language.toUpperCase()}` : ""}</small><strong>{card.title}</strong><p>{card.release_year ?? (card.media_type === "movie" ? "Movie" : "Series")} · {card.video_name}</p></div>
        </Link>)}</div> : <p className={styles.muted}>No playable videos matched these filters. Try another combination.</p>}
      </section>
      <nav className={styles.actions} aria-label="More trailer results" style={{justifyContent:"center",marginTop:28}}>
        {payload.page > 1 ? <Link className={styles.buttonSecondary} href={link(query,payload.page-1)}>← Previous</Link> : null}
        {payload.has_more ? <Link className={styles.buttonSecondary} href={link(query,payload.page+1)}>More trailers →</Link> : null}
      </nav>
    </>}
  </main>;
}
