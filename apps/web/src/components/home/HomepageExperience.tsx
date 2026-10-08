"use client";
/* eslint-disable @next/next/no-img-element */

import type {
  HomeGenreEntry,
  HomeGenresResponse,
  HomeHeroExperience,
  HomeItem,
  HomeRailResponse,
  HomeResponse,
  HomeTrailerRailResponse,
} from "@cinewatch/contracts";
import Link from "next/link";
import { useEffect, useRef, useState } from "react";

import { MediaTypeIcon, RatingSourceLogo } from "@/components/catalog/MediaIdentity";
import GenreCard from "@/components/catalog/GenreCard";

import styles from "./HomepageExperience.module.css";

type Props = { initialHome: HomeResponse | null };
type RemoteState = "idle" | "loading" | "ready" | "empty" | "error";

const additionalRails = [
  "upcoming",
  "bollywood",
  "nollywood",
  "chinese",
  "hollywood",
  "documentaries",
  "reality",
] as const;

function yearFromDate(value: string | null | undefined): string | null {
  if (!value) return null;
  const match = /^(\d{4})/.exec(value);
  return match?.[1] ?? null;
}


function entityPath(item: HomeItem): string {
  if (item.future_path) return item.future_path;
  return item.media_type === "person"
    ? `/person/${item.provider_id}`
    : `/title/${item.media_type}/${item.provider_id}`;
}

function discoverySlug(title: string): string {
  return title.toLocaleLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
}

export default function HomepageExperience({ initialHome }: Props) {
  const hero = initialHome?.hero ?? null;
  const [heroExperience, setHeroExperience] = useState<HomeHeroExperience | null>(null);
  const [heroState, setHeroState] = useState<RemoteState>(hero ? (hero.media_type === "person" ? "ready" : "loading") : "empty");
  const [expandedSynopsis, setExpandedSynopsis] = useState(false);

  useEffect(() => {
    if (!hero || hero.media_type === "person") return;
    const controller = new AbortController();
    fetch(`/api/cinewatch/home/hero/${hero.media_type}/${hero.provider_id}`, {
      cache: "no-store",
      signal: controller.signal,
    })
      .then(async (response) => {
        if (!response.ok) throw new Error(`hero ${response.status}`);
        return await response.json() as HomeHeroExperience;
      })
      .then((payload) => {
        setHeroExperience(payload);
        setHeroState("ready");
      })
      .catch(() => {
        if (!controller.signal.aborted) setHeroState("error");
      });
    return () => controller.abort();
  }, [hero]);

  if (!initialHome) {
    return (
      <section className={styles.unavailable}>
        <img src="/brand/cinewatch-lockup-on-dark.svg" alt="CineWatch TV" />
        <h1>CineWatch could not load the catalogue.</h1>
        <p>Please try again shortly.</p>
      </section>
    );
  }

  return (
    <div className={styles.home}>
      {hero ? (
        <Hero
          hero={hero}
          experience={heroExperience}
          experienceState={heroState}
          expandedSynopsis={expandedSynopsis}
          onToggleSynopsis={() => setExpandedSynopsis((value) => !value)}
        />
      ) : null}

      <section className={styles.section}>
        <SectionHeading title="Stream Now" />
        <Link className={styles.streamCallout} href="/under-development/stream-now">
          <span className={styles.streamMark}>C</span>
          <span><strong>Stream Now is under development</strong><small>Playback will appear here when CineWatch content is ready.</small></span>
          <b>View status →</b>
        </Link>
      </section>

      <ContentRail title="Trending Now" items={initialHome.sections.trending ?? []} />
      <ContentRail title="Popular Movies" items={initialHome.sections.popular_movies ?? []} />
      <ContentRail title="Popular TV Shows" items={initialHome.sections.popular_tv ?? []} />

      <LazyRail slug="k-drama" />
      <LazyRail slug="kenyan-stories" />
      <LazyRail slug="tyler-perry" />
      <LazyTrailerRail />
      <LazyGenres />
      {additionalRails.map((slug) => <LazyRail key={slug} slug={slug} />)}

      <section className={styles.section}>
        <SectionHeading title="Entertainment News" destination="/news" />
        <Link className={styles.newsCallout} href="/news">Open CineWatch News →</Link>
      </section>
    </div>
  );
}

function Hero({
  hero,
  experience,
  experienceState,
  expandedSynopsis,
  onToggleSynopsis,
}: {
  hero: HomeItem;
  experience: HomeHeroExperience | null;
  experienceState: RemoteState;
  expandedSynopsis: boolean;
  onToggleSynopsis: () => void;
}) {
  const background = hero.backdrop_url ?? hero.poster_url ?? "";
  const synopsis = hero.overview ?? "";
  const shouldCollapse = synopsis.length > 280;
  const visibleSynopsis = !expandedSynopsis && shouldCollapse ? `${synopsis.slice(0, 278).trimEnd()}…` : synopsis;
  const releaseYear = yearFromDate(hero.date);
  const titlePath = entityPath(hero);
  const trailerPath = hero.media_type === "person" || !experience?.trailer ? null : `/title/${hero.media_type}/${hero.provider_id}/trailers`;

  return (
    <section className={styles.hero} style={background ? { backgroundImage: `url(${background})` } : undefined} aria-label={`Featured: ${hero.title}`}>
      <div className={styles.heroShade} />
      <div className={styles.heroContent}>
        {hero.poster_url ? <img className={styles.heroPoster} src={hero.poster_url} alt={`${hero.title} poster`} /> : null}
        <div className={styles.heroCopy}>
          <span className={styles.trendingLabel}>Trending Now</span>
          <h1>{hero.title}</h1>
          <div className={styles.heroMeta}>{releaseYear ? <span>{releaseYear}</span> : null}{hero.media_type !== "person" ? <MediaTypeIcon mediaType={hero.media_type} withLabel /> : <span>Person</span>}</div>
          <div className={styles.ratings} aria-label="Ratings">
            {experience?.ratings?.map((rating) => <span key={rating.source} className={styles.ratingBadge}><RatingSourceLogo source={rating.source} /><span>{rating.display_value}</span></span>)}
            {hero.rating ? <span className={styles.ratingBadge}><RatingSourceLogo source="tmdb" /><span>{hero.rating.value.toFixed(1)}/10</span></span> : null}
          </div>
          {experience?.quote ? <blockquote>“{experience.quote}”</blockquote> : null}
          {synopsis ? <div className={styles.synopsis}><p>{visibleSynopsis}</p>{shouldCollapse ? <button type="button" aria-expanded={expandedSynopsis} onClick={onToggleSynopsis}>{expandedSynopsis ? "Less" : "More"}</button> : null}</div> : null}
          {experience?.writers?.length ? <p className={styles.writers}><span>Written / Created by</span> {experience.writers.join(", ")}</p> : null}
          {experienceState === "error" ? <p className={styles.heroProviderError}>More details could not be loaded right now.</p> : null}
          <div className={styles.heroActions}>
            {trailerPath ? <Link className={styles.primaryAction} href={trailerPath}>▶ Watch Trailer</Link> : null}
            <Link className={styles.secondaryAction} href={titlePath}>More Info</Link>
            <Link className={styles.secondaryAction} href="/under-development/my-list">＋ My List</Link>
          </div>
        </div>
      </div>
    </section>
  );
}

function SectionHeading({ title, note, destination }: { title: string; note?: string; destination?: string }) {
  return <div className={styles.sectionHeading}><div><h2>{title}</h2>{note ? <p>{note}</p> : null}</div>{destination ? <Link href={destination} className={styles.seeAll}>See All →</Link> : null}</div>;
}

function ContentRail({ title, items }: { title: string; items: HomeItem[] }) {
  if (!items.length) return null;
  return <section className={styles.section}><SectionHeading title={title} destination={`/discover/${discoverySlug(title)}`} /><div className={styles.rail}>{items.map((item) => <MediaCard key={`${item.media_type}-${item.provider_id}`} item={item} />)}</div></section>;
}

function MediaCard({ item }: { item: HomeItem }) {
  const art = item.backdrop_url ?? item.poster_url;
  return (
    <Link href={entityPath(item)} className={styles.card} data-provider-id={item.provider_id} data-media-type={item.media_type} data-genre-ids={(item.genre_ids ?? []).join(",")}>
      <div className={styles.cardArt}>{art ? <img src={art} alt="" loading="lazy" /> : <div className={styles.noArt}>C</div>}{item.rating ? <span className={styles.cardScore}>{item.rating.value.toFixed(1)}</span> : null}</div>
      <strong>{item.title}</strong><small className={styles.cardMeta}>{yearFromDate(item.date) ? <span>{yearFromDate(item.date)}</span> : null}{item.media_type !== "person" ? <MediaTypeIcon mediaType={item.media_type} withLabel /> : <span>Person</span>}</small>
    </Link>
  );
}

function useIntersectionStart(ref: React.RefObject<HTMLElement | null>, started: boolean, onStart: () => void) {
  useEffect(() => {
    const node = ref.current;
    if (!node || started) return;
    const observer = new IntersectionObserver((entries) => {
      if (!entries.some((entry) => entry.isIntersecting)) return;
      observer.disconnect();
      onStart();
    }, { rootMargin: "700px 0px" });
    observer.observe(node);
    return () => observer.disconnect();
  }, [ref, started, onStart]);
}

function LazyRail({ slug }: { slug: string }) {
  const ref = useRef<HTMLElement | null>(null);
  const [payload, setPayload] = useState<HomeRailResponse | null>(null);
  const [state, setState] = useState<RemoteState>("idle");
  function load() {
    setState("loading");
    fetch(`/api/cinewatch/home/rails/${slug}`, { cache: "no-store" })
      .then(async (response) => { if (!response.ok) throw new Error(`rail ${response.status}`); return await response.json() as HomeRailResponse; })
      .then((value) => { setPayload(value); setState(value.items?.length ? "ready" : "empty"); })
      .catch(() => { setPayload(null); setState("error"); });
  }
  useIntersectionStart(ref, state !== "idle", load);
  if (state === "empty") return null;
  return (
    <section ref={ref} className={styles.section} data-lazy-rail={slug}>
      {state === "ready" && payload ? <><SectionHeading title={payload.title} destination={`/discover/${slug}`} /><div className={styles.rail}>{(payload.items ?? []).map((item) => <MediaCard key={`${item.media_type}-${item.provider_id}`} item={item} />)}</div></> : null}
      {state === "idle" || state === "loading" ? <RailSkeleton /> : null}
      {state === "error" ? <RailFailure label={slug.replaceAll("-", " ")} onRetry={load} /> : null}
    </section>
  );
}

function LazyGenres() {
  const ref = useRef<HTMLElement | null>(null);
  const [genres, setGenres] = useState<HomeGenreEntry[]>([]);
  const [state, setState] = useState<RemoteState>("idle");
  function load() {
    setState("loading");
    fetch("/api/cinewatch/home/genres", { cache: "no-store" })
      .then(async (response) => { if (!response.ok) throw new Error(`genres ${response.status}`); return await response.json() as HomeGenresResponse; })
      .then((payload) => { const next = payload.genres ?? []; setGenres(next); setState(next.length ? "ready" : "empty"); })
      .catch(() => { setGenres([]); setState("error"); });
  }
  useIntersectionStart(ref, state !== "idle", load);
  if (state === "empty") return null;
  return <section ref={ref} className={styles.section}>{state === "ready" ? <><SectionHeading title="Genres" destination="/genres" /><div className={styles.genreGrid}>{genres.slice(0, 8).map((genre) => <GenreCard key={genre.slug} genre={genre} />)}</div></> : null}{state === "idle" || state === "loading" ? <RailSkeleton /> : null}{state === "error" ? <RailFailure label="genres" onRetry={load} /> : null}</section>;
}

function LazyTrailerRail() {
  const ref = useRef<HTMLElement | null>(null);
  const [payload, setPayload] = useState<HomeTrailerRailResponse | null>(null);
  const [state, setState] = useState<RemoteState>("idle");
  function load() {
    setState("loading");
    fetch("/api/cinewatch/home/trailers", { cache: "no-store" })
      .then(async (response) => { if (!response.ok) throw new Error(`trailers ${response.status}`); return await response.json() as HomeTrailerRailResponse; })
      .then((value) => { setPayload(value); setState(value.items?.length ? "ready" : "empty"); })
      .catch(() => { setPayload(null); setState("error"); });
  }
  useIntersectionStart(ref, state !== "idle", load);
  if (state === "empty") return null;
  return (
    <section ref={ref} className={styles.section}>
      {state === "ready" && payload ? <><SectionHeading title={payload.title} /><div className={styles.trailerRail}>{(payload.items ?? []).map(({ item, trailer }) => { const art = item.backdrop_url ?? item.poster_url; return <Link key={`${item.media_type}-${item.provider_id}-${trailer.youtube_key}`} href={`/title/${item.media_type}/${item.provider_id}/trailers`} className={styles.trailerCard}>{art ? <img src={art} alt="" loading="lazy" /> : null}<span className={styles.playDisc}>▶</span><strong>{item.title}</strong><small>YouTube · {trailer.video_type}</small></Link>; })}</div></> : null}
      {state === "idle" || state === "loading" ? <RailSkeleton /> : null}
      {state === "error" ? <RailFailure label="trailers" onRetry={load} /> : null}
    </section>
  );
}

function RailFailure({ label, onRetry }: { label: string; onRetry: () => void }) {
  return <div className={styles.railError}><strong>{label.charAt(0).toUpperCase() + label.slice(1)} could not be loaded.</strong><span>Try again in a moment.</span><button type="button" onClick={onRetry}>Retry</button></div>;
}

function RailSkeleton() {
  return <div className={styles.skeletonWrap} aria-label="Loading section"><div className={styles.skeletonTitle} /><div className={styles.skeletonRail}>{Array.from({ length: 6 }, (_, index) => <span key={index} />)}</div></div>;
}
