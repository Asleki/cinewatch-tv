import styles from "@/app/r3-page.module.css";
import { getPublicApiBaseUrl } from "@/lib/config/public-env";

type Match = { title: string; year: number | null; source: string | null; script_url: string | null; download_url: string | null; writers: string[]; genres: string[]; script_format: string | null; has_script_text: boolean; word_count: number | null; scene_count: number | null; excerpt: string | null };
type Payload = { requested_title: string; resolved: boolean; ambiguous: boolean; candidate_count: number; match: Match | null };

async function load(title: string, year: string): Promise<Payload | null> {
  try {
    const url = new URL("/api/v1/external/scripts", getPublicApiBaseUrl());
    url.searchParams.set("title", title); if (/^\d{4}$/.test(year)) url.searchParams.set("year", year);
    const response = await fetch(url, { cache: "no-store", headers: { Accept: "application/json" } });
    if (!response.ok) return null;
    return await response.json() as Payload;
  } catch { return null; }
}

export default async function ScriptsPage({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  const query = await searchParams;
  const title = typeof query.title === "string" ? query.title.trim() : "";
  const year = typeof query.year === "string" ? query.year.trim() : "";
  const payload = title ? await load(title, year) : null;
  return <main className={styles.page}>
    <section className={styles.hero}><p className={styles.eyebrow}>Screenplay Reference</p><h1>Scripts</h1><p>Search is title-bound. Same-name or conflicting screenplay matches remain unresolved instead of being attached to the wrong film.</p><form className={styles.form} method="get" action="/scripts"><input name="title" defaultValue={title} placeholder="Movie title" aria-label="Movie title" /><input name="year" defaultValue={year} inputMode="numeric" pattern="[0-9]{4}" placeholder="Year (optional)" aria-label="Year" /><button type="submit">Find script</button></form></section>
    {title ? !payload ? <section className={styles.section}><div className={styles.error}><strong>Script information could not be loaded.</strong></div></section> : !payload.resolved ? <section className={styles.section}><p className={styles.muted}>{payload.ambiguous ? "Multiple exact screenplay matches remain, so CineWatch left this search unresolved." : "No exact screenplay match was found."}</p></section> : payload.match ? <section className={styles.section}><div className={styles.sectionHead}><div><p className={styles.eyebrow}>{payload.match.source || "Public screenplay source"}</p><h2>{payload.match.title}{payload.match.year ? ` (${payload.match.year})` : ""}</h2></div></div><div className={styles.card}><div className={styles.cardBody}>{payload.match.writers.length ? <p>Written by {payload.match.writers.join(", ")}</p> : null}{payload.match.excerpt ? <p>{payload.match.excerpt}</p> : null}<div className={styles.actions}>{payload.match.script_url ? <a className={styles.button} href={payload.match.script_url} target="_blank" rel="noopener noreferrer">Open public source</a> : null}{payload.match.download_url ? <a className={styles.buttonSecondary} href={payload.match.download_url} target="_blank" rel="noopener noreferrer">Open public file</a> : null}</div></div></div></section> : null : null}
  </main>;
}
