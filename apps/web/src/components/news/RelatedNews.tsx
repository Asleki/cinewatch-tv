"use client";
/* eslint-disable @next/next/no-img-element */

import { useEffect, useState } from "react";

import styles from "./RelatedNews.module.css";

type Article = {
  source: { name: string };
  title: string;
  description: string | null;
  article_url: string;
  image_url: string | null;
  published_at: string | null;
};

type NewsResponse = { articles: Article[] };
type State = "loading" | "ready" | "empty" | "error";

export default function RelatedNews({ query, heading = "In the News" }: { query: string; heading?: string }) {
  const [state, setState] = useState<State>("loading");
  const [articles, setArticles] = useState<Article[]>([]);
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    const controller = new AbortController();
    const startTimer = window.setTimeout(() => {
      setState("loading");
      const params = new URLSearchParams({ q: query, page_size: "3" });
      fetch(`/api/cinewatch/news?${params.toString()}`, { cache: "no-store", signal: controller.signal, headers: { Accept: "application/json" } })
        .then(async (response) => {
          if (!response.ok) throw new Error(`news ${response.status}`);
          return await response.json() as NewsResponse;
        })
        .then((payload) => {
          const next = payload.articles ?? [];
          setArticles(next);
          setState(next.length ? "ready" : "empty");
        })
        .catch(() => {
          if (!controller.signal.aborted) {
            setArticles([]);
            setState("error");
          }
        });
    }, 0);
    return () => {
      window.clearTimeout(startTimer);
      controller.abort();
    };
  }, [query, attempt]);

  if (state === "empty") return null;
  return (
    <section className={styles.section}>
      <div className={styles.head}><div><p>CineWatch News</p><h2>{heading}</h2></div><a href={`/news?q=${encodeURIComponent(query)}`}>More news →</a></div>
      {state === "loading" ? <p className={styles.muted}>Loading live news…</p> : null}
      {state === "error" ? <div className={styles.failure}><strong>News could not be loaded.</strong><span>Try again in a moment.</span><button type="button" onClick={() => setAttempt((value) => value + 1)}>Retry</button></div> : null}
      {state === "ready" ? <div className={styles.grid}>{articles.map((article) => <a key={article.article_url} href={article.article_url} target="_blank" rel="noopener noreferrer">{article.image_url ? <img src={article.image_url} alt="" loading="lazy" /> : null}<div><small>{article.source.name}{article.published_at ? ` · ${article.published_at.slice(0, 10)}` : ""}</small><strong>{article.title}</strong>{article.description ? <p>{article.description}</p> : null}</div></a>)}</div> : null}
    </section>
  );
}
