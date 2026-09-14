"use client";
/* eslint-disable @next/next/no-img-element */

import type { CatalogSeasonResponse, CatalogTitleResponse } from "@cinewatch/contracts";
import Link from "next/link";
import { useState } from "react";

import CatalogCard from "./CatalogCard";
import styles from "./TitleDetails.module.css";

type Props = { title: CatalogTitleResponse; fullView?: boolean };

function sourceLabel(source: string) {
  if (source === "tmdb") return "TMDb";
  if (source === "imdb") return "IMDb";
  if (source === "rotten_tomatoes") return "RT";
  return "MC";
}

export default function TitleDetails({ title, fullView = false }: Props) {
  const [trailerOpen, setTrailerOpen] = useState(false);
  const [openSeason, setOpenSeason] = useState<number | null>(null);
  const [seasonPayload, setSeasonPayload] = useState<Record<number, CatalogSeasonResponse | null>>({});
  const [seasonStatus, setSeasonStatus] = useState<Record<number, "loading" | "ready" | "error">>({});
  const [castExpanded, setCastExpanded] = useState(false);

  async function toggleSeason(seasonNumber: number) {
    if (openSeason === seasonNumber) { setOpenSeason(null); return; }
    setOpenSeason(seasonNumber);
    if (seasonStatus[seasonNumber] === "loading" || seasonStatus[seasonNumber] === "ready") return;
    setSeasonStatus((current) => ({ ...current, [seasonNumber]: "loading" }));
    try {
      const response = await fetch(`/api/cinewatch/catalog/title/tv/${title.provider_id}/season/${seasonNumber}`, { cache: "no-store" });
      if (!response.ok) throw new Error("season unavailable");
      const payload = await response.json() as CatalogSeasonResponse;
      setSeasonPayload((current) => ({ ...current, [seasonNumber]: payload }));
      setSeasonStatus((current) => ({ ...current, [seasonNumber]: "ready" }));
    } catch {
      setSeasonPayload((current) => ({ ...current, [seasonNumber]: null }));
      setSeasonStatus((current) => ({ ...current, [seasonNumber]: "error" }));
    }
  }

  const visibleCast = castExpanded ? (title.cast ?? []) : (title.cast ?? []).slice(0, 8);

  return (
    <main>
      <section className={styles.hero} style={title.backdrop_url ? { backgroundImage: `url(${title.backdrop_url})` } : undefined}>
        <div className={styles.heroShade} />
        <div className={styles.heroInner}>
          {title.poster_url ? <img className={styles.poster} src={title.poster_url} alt={`${title.title} poster`} /> : null}
          <div className={styles.heroCopy}>
            <p className={styles.eyebrow}>{title.media_type === "tv" ? "TV Series" : "Movie"}</p>
            <h1>{title.title}</h1>
            {title.tagline ? <p className={styles.tagline}>{title.tagline}</p> : null}
            <div className={styles.meta}><span>{title.year ?? "Year unavailable"}</span>{title.runtime_minutes ? <span>{title.runtime_minutes} min</span> : null}{title.status ? <span>{title.status}</span> : null}</div>
            <div className={styles.ratings}>{(title.ratings ?? []).map((rating) => <span key={rating.source}><b>{sourceLabel(rating.source)}</b> {rating.display_value}</span>)}</div>
            <p className={styles.overview}>{title.overview || "Synopsis unavailable."}</p>
            {(title.creators ?? []).length ? <p className={styles.peopleLine}><b>Created by</b> {(title.creators ?? []).join(", ")}</p> : null}
            {(title.writers ?? []).length ? <p className={styles.peopleLine}><b>Written by</b> {(title.writers ?? []).join(", ")}</p> : null}
            <div className={styles.actions}>
              {title.trailer ? <button type="button" onClick={() => setTrailerOpen(true)}>▶ Watch Trailer</button> : null}
              <a href="#cast">Cast</a>
              {title.review_count ? <Link href={`/title/${title.media_type}/${title.provider_id}/reviews`}>Reviews</Link> : null}
            </div>
            {(title.networks ?? []).length || (title.watch_providers ?? []).length ? (
              <div className={styles.providers}>
                {(title.networks ?? []).slice(0, 5).map((network) => <span key={`n-${network.provider_id ?? network.name}`}>{network.logo_url ? <img src={network.logo_url} alt={network.name} title={network.name} /> : network.name}</span>)}
                {(title.watch_providers ?? []).slice(0, 6).map((provider) => <span key={`w-${provider.provider_id}`}>{provider.logo_url ? <img src={provider.logo_url} alt={provider.name} title={`${provider.name} · ${provider.monetization_type}`} /> : provider.name}</span>)}
              </div>
            ) : null}
            {title.watch_information_url ? <a className={styles.watchInfoLink} href={title.watch_information_url} target="_blank" rel="noreferrer">View streaming options ↗</a> : null}
          </div>
        </div>
      </section>

      <div className={styles.body}>
        <section className={styles.factBar}>
          {(title.genres ?? []).map((genre) => <Link key={genre} href={`/genre/${genre.toLocaleLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "")}`}>{genre}</Link>)}
          {title.original_language ? <span>Language: {title.original_language.toUpperCase()}</span> : null}
          {title.awards && title.awards !== "N/A" ? <span>{title.awards}</span> : null}
          {title.box_office && title.box_office !== "N/A" ? <span>Box office: {title.box_office}</span> : null}
        </section>

        <section id="cast" className={styles.section}>
          <div className={styles.sectionHead}><div><p>People</p><h2>Top Cast</h2></div>{(title.cast ?? []).length > 8 ? <button type="button" onClick={() => setCastExpanded((value) => !value)}>{castExpanded ? "Show less" : "View all cast"}</button> : null}</div>
          <div className={styles.castGrid}>{visibleCast.map((member) => <Link key={member.provider_id} href={member.future_path}><span>{member.profile_url ? <img src={member.profile_url} alt="" loading="lazy" /> : "C"}</span><strong>{member.name}</strong><small>{member.character || "Role unavailable"}</small></Link>)}</div>
        </section>

        {fullView ? (
          <section className={styles.section}>
            <div className={styles.sectionHead}><div><p>Production</p><h2>Full Details</h2></div></div>
            <div className={styles.fullFacts}>
              {title.production_budget != null && title.production_budget > 0 ? <span><b>Budget</b>${title.production_budget.toLocaleString()}</span> : null}
              {title.revenue != null && title.revenue > 0 ? <span><b>Revenue</b>${title.revenue.toLocaleString()}</span> : null}
              {title.box_office && title.box_office !== "N/A" ? <span><b>Box office</b>{title.box_office}</span> : null}
              {title.awards && title.awards !== "N/A" ? <span><b>Awards</b>{title.awards}</span> : null}
            </div>
            {(title.crew ?? []).length ? <div className={styles.crewGrid}>{(title.crew ?? []).map((member) => <Link key={`${member.provider_id}-${member.job ?? member.department ?? "crew"}`} href={member.future_path}>{member.profile_url ? <img src={member.profile_url} alt="" loading="lazy" /> : <span>C</span>}<strong>{member.name}</strong><small>{member.job || member.department || "Crew"}</small></Link>)}</div> : null}
          </section>
        ) : null}

        {title.media_type === "tv" && (title.seasons ?? []).length ? (
          <section className={styles.section}>
            <div className={styles.sectionHead}><div><p>Episodes</p><h2>Seasons</h2></div></div>
            <div className={styles.seasons}>
              {(title.seasons ?? []).filter((season) => season.season_number > 0).map((season) => (
                <article key={season.season_number}>
                  <button type="button" onClick={() => toggleSeason(season.season_number)} aria-expanded={openSeason === season.season_number}>
                    <span>{season.poster_url ? <img src={season.poster_url} alt="" loading="lazy" /> : null}</span>
                    <span><strong>{season.name}</strong><small>{season.episode_count} episodes{season.air_date ? ` · ${season.air_date.slice(0,4)}` : ""}</small></span>
                    <b>{openSeason === season.season_number ? "−" : "+"}</b>
                  </button>
                  {openSeason === season.season_number ? (
                    <div className={styles.episodes}>
                      {seasonStatus[season.season_number] === "error" ? <p>Episodes are unavailable right now. Try this season again.</p> : seasonStatus[season.season_number] === "ready" ? (seasonPayload[season.season_number]?.episodes?.length ? (seasonPayload[season.season_number]?.episodes ?? []).map((episode) => <div key={episode.provider_id}>{episode.still_url ? <img src={episode.still_url} alt="" loading="lazy" /> : null}<span><strong>{episode.episode_number}. {episode.name}</strong><small>{episode.air_date || "Air date unavailable"}</small><p>{episode.overview || "Episode synopsis unavailable."}</p></span></div>) : <p>No episodes are listed for this season.</p>) : <p>Loading episodes…</p>}
                    </div>
                  ) : null}
                </article>
              ))}
            </div>
          </section>
        ) : null}

        {(title.reviews ?? []).length ? (
          <section className={styles.section}>
            <div className={styles.sectionHead}><div><p>Community</p><h2>Reviews</h2></div><Link href={`/title/${title.media_type}/${title.provider_id}/reviews`}>Read more reviews</Link></div>
            <div className={styles.reviews}>{(title.reviews ?? []).map((review) => <details key={review.provider_review_id}><summary><strong>{review.author}</strong>{review.rating != null ? <span>{review.rating.toFixed(1)}/10</span> : null}</summary><p>{review.content}</p></details>)}</div>
          </section>
        ) : null}

        {(title.recommendations ?? []).length ? (
          <section className={styles.section}>
            <div className={styles.sectionHead}><div><p>Keep discovering</p><h2>Recommended</h2></div></div>
            <div className={styles.recommendations}>{(title.recommendations ?? []).map((item) => <CatalogCard key={`${item.media_type}-${item.provider_id}`} item={item} />)}</div>
          </section>
        ) : null}
      </div>

      {trailerOpen && title.trailer ? <div className={styles.modalBackdrop} onMouseDown={(event) => { if (event.target === event.currentTarget) setTrailerOpen(false); }}><section className={styles.modal} role="dialog" aria-modal="true" aria-label={`${title.title} trailer`}><header><div><strong>{title.title}</strong><small>{title.trailer.name}</small></div><button type="button" onClick={() => setTrailerOpen(false)} aria-label="Close trailer">×</button></header><iframe src={`https://www.youtube-nocookie.com/embed/${encodeURIComponent(title.trailer.youtube_key)}?autoplay=1&rel=0`} title={`${title.title} trailer`} allow="autoplay; encrypted-media; picture-in-picture" allowFullScreen /></section></div> : null}
    </main>
  );
}
