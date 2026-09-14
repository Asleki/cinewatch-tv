import styles from "@/app/r3-page.module.css";
import { getPublicApiBaseUrl } from "@/lib/config/public-env";

type Match = { song: string; artist: string; album: string | null; song_url: string | null; artist_url: string | null; album_url: string | null };
type Payload = { term: string; artist: string; album: string | null; resolved: boolean; ambiguous: boolean; match: Match | null; candidates: Match[]; candidate_count: number };

async function load(term: string, artist: string, album: string, referenceUrl: string): Promise<Payload | null> {
  try {
    const url = new URL("/api/v1/external/lyrics", getPublicApiBaseUrl());
    url.searchParams.set("term", term);
    url.searchParams.set("artist", artist);
    if (album) url.searchParams.set("album", album);
    if (referenceUrl) url.searchParams.set("reference_url", referenceUrl);
    const response = await fetch(url, { cache: "no-store", headers: { Accept: "application/json" } });
    if (!response.ok) return null;
    return await response.json() as Payload;
  } catch { return null; }
}

export default async function LyricsPage({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  const query = await searchParams;
  const term = typeof query.term === "string" ? query.term.trim() : "";
  const artist = typeof query.artist === "string" ? query.artist.trim() : "";
  const album = typeof query.album === "string" ? query.album.trim() : "";
  const referenceUrl = typeof query.reference_url === "string" ? query.reference_url.trim() : "";
  const payload = term && artist ? await load(term, artist, album, referenceUrl) : null;
  const candidates = payload?.candidates ?? [];
  return <main className={styles.page}>
    <section className={styles.hero}><p className={styles.eyebrow}>Music Reference</p><h1>Lyrics & Songs</h1><p>Search uses the exact song and artist. Album can narrow a release. CineWatch never chooses between same-name records by guesswork.</p><form className={styles.form} method="get" action="/lyrics"><input name="term" defaultValue={term} placeholder="Song title" aria-label="Song title" /><input name="artist" defaultValue={artist} placeholder="Artist" aria-label="Artist" /><input name="album" defaultValue={album} placeholder="Album (optional)" aria-label="Album" /><button type="submit">Find song</button></form></section>
    {term && artist && !payload ? <section className={styles.section}><div className={styles.error}><strong>Song information could not be loaded.</strong></div></section> : null}
    {payload && !payload.resolved && payload.ambiguous ? <section className={styles.section}><div className={styles.sectionHead}><h2>Choose the matching release</h2></div><p className={styles.muted}>{payload.candidate_count} exact provider records remain. Select the exact reference instead of letting CineWatch guess.</p><div className={styles.grid}>{candidates.map((candidate) => { const params = new URLSearchParams({ term, artist }); if (album) params.set("album", album); if (candidate.song_url) params.set("reference_url", candidate.song_url); return <article className={styles.card} key={candidate.song_url ?? `${candidate.song}-${candidate.album ?? ""}`}><div className={styles.cardBody}><small>{candidate.artist}</small><strong>{candidate.song}</strong><p>{candidate.album || "Album not specified"}</p><div className={styles.actions}>{candidate.song_url ? <a className={styles.button} href={`/lyrics?${params.toString()}`}>Use this result</a> : null}{candidate.song_url ? <a className={styles.buttonSecondary} href={candidate.song_url} target="_blank" rel="noopener noreferrer">Reference</a> : null}</div></div></article>; })}</div></section> : null}
    {payload && !payload.resolved && !payload.ambiguous ? <section className={styles.section}><p className={styles.muted}>No exact song-and-artist match was found.</p></section> : null}
    {payload?.resolved && payload.match ? <section className={styles.section}><div className={styles.sectionHead}><h2>{payload.match.song}</h2></div><div className={styles.card}><div className={styles.cardBody}><small>{payload.match.artist}</small><strong>{payload.match.album || "Album not specified"}</strong><div className={styles.actions}>{payload.match.song_url ? <a className={styles.button} href={payload.match.song_url} target="_blank" rel="noopener noreferrer">Open song reference</a> : null}{payload.match.artist_url ? <a className={styles.buttonSecondary} href={payload.match.artist_url} target="_blank" rel="noopener noreferrer">Artist</a> : null}</div></div></div></section> : null}
  </main>;
}
