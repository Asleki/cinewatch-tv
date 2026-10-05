"use client";
/* eslint-disable @next/next/no-img-element */

import type { CatalogSeasonResponse, CatalogTitleResponse } from "@cinewatch/contracts";
import Link from "next/link";
import { useState } from "react";

import RelatedNews from "@/components/news/RelatedNews";

import CatalogCard from "./CatalogCard";
import { MediaTypeIcon, RatingSourceLogo } from "./MediaIdentity";
import styles from "./TitleDetails.module.css";

type Props = { title: CatalogTitleResponse; fullView?: boolean };
type SeasonState = "idle" | "loading" | "ready" | "empty" | "error";


function lifecycleLabel(status: string | null | undefined, mediaType: string) {
  if (!status) return null;
  if (mediaType !== "tv") return status;
  const normalized: Record<string, string> = {
    "Returning Series": "Returning series",
    "Ended": "Series ended",
    "Canceled": "Series canceled",
    "In Production": "In production",
    "Planned": "Planned series",
    "Pilot": "Pilot",
  };
  return normalized[status] ?? status;
}

export default function TitleDetails({ title, fullView = false }: Props) {
  const [openSeason, setOpenSeason] = useState<number | null>(null);
  const [seasonPayload, setSeasonPayload] = useState<Record<number, CatalogSeasonResponse | null>>({});
  const [seasonStatus, setSeasonStatus] = useState<Record<number, SeasonState>>({});
  const [castExpanded, setCastExpanded] = useState(false);

  async function loadSeason(seasonNumber: number, force = false) {
    const status = seasonStatus[seasonNumber] ?? "idle";
    if (!force && (status === "loading" || status === "ready" || status === "empty")) return;
    setSeasonStatus((current) => ({ ...current, [seasonNumber]: "loading" }));
    try {
      const response = await fetch(`/api/cinewatch/catalog/title/tv/${title.provider_id}/season/${seasonNumber}`, { cache: "no-store" });
      if (!response.ok) throw new Error(`season ${response.status}`);
      const payload = await response.json() as CatalogSeasonResponse;
      setSeasonPayload((current) => ({ ...current, [seasonNumber]: payload }));
      setSeasonStatus((current) => ({ ...current, [seasonNumber]: payload.episodes?.length ? "ready" : "empty" }));
    } catch {
      setSeasonPayload((current) => ({ ...current, [seasonNumber]: null }));
      setSeasonStatus((current) => ({ ...current, [seasonNumber]: "error" }));
    }
  }

  async function toggleSeason(seasonNumber: number) {
    if (openSeason === seasonNumber) {
      setOpenSeason(null);
      return;
    }
    setOpenSeason(seasonNumber);
    await loadSeason(seasonNumber);
  }

  const cast = title.cast ?? [];
  const creators = title.creators ?? [];
  const writers = title.writers ?? [];
  const crew = title.crew ?? [];
  const seasons = title.seasons ?? [];
  const reviews = title.reviews ?? [];
  const recommendations = title.recommendations ?? [];
  const ratings = title.ratings ?? [];
  const networks = title.networks ?? [];
  const watchProviders = title.watch_providers ?? [];
  const genres = title.genres ?? [];
  const visibleCast = castExpanded ? cast : cast.slice(0, 8);
  const status = lifecycleLabel(title.status, title.media_type);
  const basePath = `/title/${title.media_type}/${title.provider_id}`;

  return (
    <main>
      <section className={styles.hero} style={title.backdrop_url ? { backgroundImage: `url(${title.backdrop_url})` } : undefined}>
        <div className={styles.heroShade} />
        <div className={styles.heroInner}>
          {title.poster_url ? <img className={styles.poster} src={title.poster_url} alt={`${title.title} poster`} /> : null}
          <div className={styles.heroCopy}>
            <p className={styles.eyebrow}><MediaTypeIcon mediaType={title.media_type} withLabel /></p>
            <h1>{title.title}</h1>
            {title.tagline ? <p className={styles.tagline}>{title.tagline}</p> : null}
            <div className={styles.meta}><span>{title.year ?? "Year unavailable"}</span>{title.runtime_minutes ? <span>{title.runtime_minutes} min</span> : null}{status ? <span>{status}</span> : null}</div>
            <div className={styles.ratings}>{ratings.map((rating) => <span key={rating.source}><RatingSourceLogo source={rating.source} /><b>{rating.display_value}</b></span>)}</div>
            <p className={styles.overview}>{title.overview || "Synopsis unavailable."}</p>
            {creators.length ? <p className={styles.peopleLine}><b>Created by</b> {creators.join(", ")}</p> : null}
            {writers.length ? <p className={styles.peopleLine}><b>Written by</b> {writers.join(", ")}</p> : null}
            <div className={styles.actions}>
              <Link href={`${basePath}/trailers`}>▶ Watch Trailer</Link>
              {!fullView ? <Link href={`${basePath}/details`}>More Info</Link> : <Link href={basePath}>Standard view</Link>}
              <a href="#cast">Cast</a>
              {title.review_count ? <Link href={`${basePath}/reviews`}>Reviews</Link> : null}
              <Link href={`/where-to-watch?media_type=${title.media_type}&tmdb_id=${title.provider_id}&title=${encodeURIComponent(title.title)}`}>Where to Watch</Link>
              <Link href="/under-development/music-tracks">Music & Tracks</Link>
              <Link href="/under-development/stream-now">Stream Now</Link>
            </div>
            {networks.length || watchProviders.length ? (
              <div className={styles.providers} aria-label="Networks and streaming providers">
                {networks.slice(0, 5).map((network) => network.provider_id ? <Link key={`n-${network.provider_id}`} href={`/${network.kind}/${network.provider_id}`} title={network.name}>{network.logo_url ? <img src={network.logo_url} alt={`${network.name} logo`} /> : network.name}</Link> : <span key={`n-${network.name}`}>{network.name}</span>)}
                {watchProviders.slice(0, 6).map((provider) => <Link key={`w-${provider.provider_id}`} href={`/provider/${provider.provider_id}`} title={`${provider.name} · ${provider.monetization_type}`}>{provider.logo_url ? <img src={provider.logo_url} alt={`${provider.name} logo`} /> : provider.name}</Link>)}
              </div>
            ) : null}
            {watchProviders.length ? <p className={styles.providerNote}>Find it on other services.</p> : null}
          </div>
        </div>
      </section>

      <div className={styles.body}>
        <section className={styles.factBar}>
          {genres.map((genre) => <Link key={genre} href={`/genre/${genre.toLocaleLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "")}`}>{genre}</Link>)}
          {title.original_language ? <span>Language: {title.original_language.toUpperCase()}</span> : null}
          {title.awards && title.awards !== "N/A" ? <span>{title.awards}</span> : null}
          {title.box_office && title.box_office !== "N/A" ? <span>Box office: {title.box_office}</span> : null}
        </section>

        <section id="cast" className={styles.section}>
          <div className={styles.sectionHead}><div><p>People</p><h2>Top Cast</h2></div>{cast.length > 8 ? <button type="button" onClick={() => setCastExpanded((value) => !value)}>{castExpanded ? "Show less" : "View all cast"}</button> : null}</div>
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
              {status ? <span><b>Status</b>{status}</span> : null}
            </div>
            {crew.length ? <div className={styles.crewGrid}>{crew.map((member) => <Link key={`${member.provider_id}-${member.job ?? member.department ?? "crew"}`} href={member.future_path}>{member.profile_url ? <img src={member.profile_url} alt="" loading="lazy" /> : <span>C</span>}<strong>{member.name}</strong><small>{member.job || member.department || "Crew"}</small></Link>)}</div> : <p className={styles.providerNote}>No production crew information is available for this title.</p>}
          </section>
        ) : null}

        {title.media_type === "tv" && seasons.length ? (
          <section className={styles.section}>
            <div className={styles.sectionHead}><div><p>Episodes</p><h2>Seasons</h2></div></div>
            <div className={styles.seasons}>
              {seasons.filter((season) => season.season_number > 0).map((season) => {
                const state = seasonStatus[season.season_number] ?? "idle";
                const payload = seasonPayload[season.season_number];
                return (
                  <article key={season.season_number}>
                    <button type="button" onClick={() => void toggleSeason(season.season_number)} aria-expanded={openSeason === season.season_number}>
                      <span>{season.poster_url ? <img src={season.poster_url} alt="" loading="lazy" /> : null}</span>
                      <span><strong>{season.name}</strong><small>{season.episode_count} episodes{season.air_date ? ` · ${season.air_date.slice(0, 4)}` : ""}</small></span>
                      <b>{openSeason === season.season_number ? "−" : "+"}</b>
                    </button>
                    {openSeason === season.season_number ? (
                      <div className={styles.episodes} data-season-state={state}>
                        {state === "idle" || state === "loading" ? <p>Loading episodes…</p> : null}
                        {state === "error" ? <div className={styles.seasonFailure}><p>Episodes could not be loaded.</p><button type="button" onClick={() => void loadSeason(season.season_number, true)}>Retry season</button></div> : null}
                        {state === "empty" ? <p>No episodes are available for this season.</p> : null}
                        {state === "ready" ? payload?.episodes?.map((episode) => <div key={episode.provider_id}>{episode.still_url ? <img src={episode.still_url} alt="" loading="lazy" /> : null}<span><strong>{episode.episode_number}. {episode.name}</strong><small>{episode.air_date || "Air date unavailable"}</small><p>{episode.overview || "Episode synopsis unavailable."}</p></span></div>) : null}
                      </div>
                    ) : null}
                  </article>
                );
              })}
            </div>
          </section>
        ) : null}

        {reviews.length ? (
          <section className={styles.section}>
            <div className={styles.sectionHead}><div><p className={styles.sourceEyebrow}><RatingSourceLogo source="tmdb" /></p><h2>Reviews</h2></div><Link href={`${basePath}/reviews`}>Read more reviews</Link></div>
            <div className={styles.reviews}>{reviews.map((review) => <details key={review.provider_review_id}><summary><strong>{review.author}</strong>{review.rating != null ? <span>{review.rating.toFixed(1)}/10</span> : null}</summary><p>{review.content}</p><small className={styles.reviewSource}><RatingSourceLogo source="tmdb" /></small></details>)}</div>
          </section>
        ) : null}

        {recommendations.length ? (
          <section className={styles.section}>
            <div className={styles.sectionHead}><div><p>Keep discovering</p><h2>Recommended</h2></div></div>
            <div className={styles.recommendations}>{recommendations.map((item) => <CatalogCard key={`${item.media_type}-${item.provider_id}`} item={item} />)}</div>
          </section>
        ) : null}

        <RelatedNews query={title.title} heading={`${title.title} in the News`} />
      </div>
    </main>
  );
}
