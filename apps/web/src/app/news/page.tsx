/* eslint-disable @next/next/no-img-element */

import styles from "@/app/r3-page.module.css";
import { getPublicApiBaseUrl } from "@/lib/config/public-env";

type Article = { source: { name: string }; author: string | null; title: string; description: string | null; article_url: string; image_url: string | null; published_at: string | null };
type NewsResponse = { query: string; page: number; page_size: number; total_results: number; articles: Article[] };

async function loadNews(query: string): Promise<{ payload: NewsResponse | null; status: number | null }> {
  try {
    const url = new URL("/api/v1/news", getPublicApiBaseUrl());
    url.searchParams.set("q", query);
    url.searchParams.set("page_size", "12");
    const response = await fetch(url, { cache: "no-store", headers: { Accept: "application/json" } });
    if (!response.ok) return { payload: null, status: response.status };
    return { payload: await response.json() as NewsResponse, status: response.status };
  } catch {
    return { payload: null, status: null };
  }
}

export default async function NewsPage({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  const queryParams = await searchParams;
  const raw = queryParams.q;
  const query = typeof raw === "string" && raw.trim() ? raw.trim().slice(0, 200) : "film OR television";
  const { payload, status } = await loadNews(query);
  return (
    <main className={styles.page}>
      <section className={styles.hero}>
        <span className={styles.chip}>CineWatch News</span>
        <p className={styles.eyebrow}>CineWatch News</p>
        <h1>Entertainment news, with its source intact.</h1>
        <p>Entertainment headlines and stories from their original publishers.</p>
        <form className={styles.form} action="/news" method="get">
          <input name="q" defaultValue={query} aria-label="News search" placeholder="Search a title, person or industry topic" />
          <button type="submit">Search News</button>
        </form>
      </section>
      {!payload ? (
        <section className={styles.section}><div className={styles.error}><strong>News is unavailable.</strong><p>CineWatch News could not be loaded{status ? ` (${status})` : ""}.</p></div></section>
      ) : payload.articles.length === 0 ? (
        <section className={styles.section}><p className={styles.muted}>No articles matched “{payload.query}”.</p></section>
      ) : (
        <section className={styles.section}>
          <div className={styles.sectionHead}><div><p className={styles.eyebrow}>Live results</p><h2>{payload.total_results.toLocaleString()} matches</h2></div></div>
          <div className={styles.grid}>
            {payload.articles.map((article) => (
              <a className={styles.card} href={article.article_url} target="_blank" rel="noopener noreferrer" key={`${article.article_url}-${article.title}`}>
                {article.image_url ? <img src={article.image_url} alt="" /> : null}
                <div className={styles.cardBody}>
                  <small>{article.source.name}{article.published_at ? ` · ${article.published_at.slice(0, 10)}` : ""}</small>
                  <strong>{article.title}</strong>
                  {article.description ? <p>{article.description}</p> : null}
                </div>
              </a>
            ))}
          </div>
        </section>
      )}
    </main>
  );
}
