"use client";
/* eslint-disable @next/next/no-img-element */

import type {
  HomeGenreEntry,
  HomeGenresResponse,
  HomeHeroExperience,
  HomeItem,
  HomeRailResponse,
  HomeResponse,
  HomeTrailer,
  HomeTrailerRailResponse,
} from "@cinewatch/contracts";
import { useEffect, useRef, useState } from "react";

import styles from "./HomepageExperience.module.css";

type Props = {
  initialHome: HomeResponse | null;
};

type TrailerModalState = {
  title: string;
  trailer: HomeTrailer;
} | null;

const regionalRails = [
  "kenyan-stories",
  "bollywood",
  "nollywood",
  "chinese",
  "hollywood",
  "documentaries",
  "reality",
  "tyler-perry",
] as const;

const streamSlots = Array.from({ length: 5 }, (_, index) => ({
  id: `stream-placeholder-${index + 1}`,
  label: "Coming to Stream Now",
}));

function yearFromDate(value: string | null | undefined): string | null {
  if (!value) return null;
  const match = /^(\d{4})/.exec(value);
  return match?.[1] ?? null;
}

function mediaLabel(item: HomeItem): string {
  if (item.media_type === "movie") return "Movie";
  if (item.media_type === "tv") return "TV";
  return "Person";
}

function futurePath(item: HomeItem): string {
  if (item.future_path) return item.future_path;
  return item.media_type === "person"
    ? `/person/${item.provider_id}`
    : `/title/${item.media_type}/${item.provider_id}`;
}

export default function HomepageExperience({ initialHome }: Props) {
  const hero = initialHome?.hero ?? null;
  const heroProviderId = hero?.provider_id ?? null;
  const heroMediaType = hero?.media_type ?? null;
  const [heroExperience, setHeroExperience] = useState<HomeHeroExperience | null>(null);
  const [expandedSynopsis, setExpandedSynopsis] = useState(false);
  const [modal, setModal] = useState<TrailerModalState>(null);

  useEffect(() => {
    if (!heroProviderId || !heroMediaType || heroMediaType === "person") return;
    const controller = new AbortController();
    fetch(`/api/cinewatch/home/hero/${heroMediaType}/${heroProviderId}`, {
      cache: "no-store",
      signal: controller.signal,
    })
      .then((response) => (response.ok ? response.json() : null))
      .then((payload) => setHeroExperience(payload))
      .catch(() => setHeroExperience(null));
    return () => controller.abort();
  }, [heroMediaType, heroProviderId]);

  if (!initialHome) {
    return (
      <section className={styles.unavailable}>
        <img src="/brand/cinewatch-lockup-on-dark.svg" alt="CineWatch TV" />
        <h1>Home is waiting for the CineWatch API.</h1>
        <p>Start the qualified API runtime on port 8000, then refresh this page.</p>
      </section>
    );
  }

  return (
    <>
      <div className={styles.home}>
        {hero ? (
          <Hero
            hero={hero}
            experience={heroExperience}
            expandedSynopsis={expandedSynopsis}
            onToggleSynopsis={() => setExpandedSynopsis((value) => !value)}
            onTrailer={(trailer) => setModal({ title: hero.title, trailer })}
          />
        ) : null}

        <section id="stream-now" className={styles.section}>
          <SectionHeading title="Stream Now" note="Content CineWatch TV is authorized to play inside CineWatch." />
          <div className={styles.streamGrid}>
            {streamSlots.map((slot) => (
              <article key={slot.id} className={styles.streamPlaceholder}>
                <span className={styles.streamMark}>C</span>
                <strong>{slot.label}</strong>
                <small>Rights-cleared playback will appear here.</small>
              </article>
            ))}
          </div>
        </section>

        <div id="discover">
          <ContentRail title="Trending Now" items={(initialHome.sections.trending ?? [])} />
          <ContentRail title="Popular Movies" items={(initialHome.sections.popular_movies ?? [])} />
          <ContentRail title="Popular TV Shows" items={(initialHome.sections.popular_tv ?? [])} />

          <LazyRail slug="upcoming" />
          <LazyRail slug="k-drama" />
          <LazyTrailerRail onTrailer={(title, trailer) => setModal({ title, trailer })} />
          <LazyGenres />

          {regionalRails.map((slug) => <LazyRail key={slug} slug={slug} />)}
        </div>
      </div>

      {modal ? (
        <TrailerModal title={modal.title} trailer={modal.trailer} onClose={() => setModal(null)} />
      ) : null}
    </>
  );
}

function Hero({
  hero,
  experience,
  expandedSynopsis,
  onToggleSynopsis,
  onTrailer,
}: {
  hero: HomeItem;
  experience: HomeHeroExperience | null;
  expandedSynopsis: boolean;
  onToggleSynopsis: () => void;
  onTrailer: (trailer: HomeTrailer) => void;
}) {
  const background = hero.backdrop_url ?? hero.poster_url ?? "";
  const synopsis = hero.overview ?? "";
  const shouldCollapse = synopsis.length > 280;
  const visibleSynopsis = !expandedSynopsis && shouldCollapse ? `${synopsis.slice(0, 278).trimEnd()}…` : synopsis;
  const releaseYear = yearFromDate(hero.date);

  return (
    <section
      className={styles.hero}
      style={background ? { backgroundImage: `url(${background})` } : undefined}
      aria-label={`Featured: ${hero.title}`}
    >
      <div className={styles.heroShade} />
      <div className={styles.heroContent}>
        {hero.poster_url ? <img className={styles.heroPoster} src={hero.poster_url} alt={`${hero.title} poster`} /> : null}
        <div className={styles.heroCopy}>
          <span className={styles.trendingLabel}>Trending Now</span>
          <h1>{hero.title}</h1>
          <div className={styles.heroMeta}>
            {releaseYear ? <span>{releaseYear}</span> : null}
            <span>{mediaLabel(hero)}</span>
          </div>
          <div className={styles.ratings} aria-label="Ratings">
            {experience?.ratings?.map((rating) => (
              <span key={rating.source} className={styles.ratingBadge}>
                <b>{rating.source === "imdb" ? "IMDb" : rating.source === "rotten_tomatoes" ? "RT" : "Meta"}</b>
                {rating.display_value}
              </span>
            ))}
            {hero.rating ? (
              <span className={styles.ratingBadge}><b>TMDb</b>{hero.rating.value.toFixed(1)}/10</span>
            ) : null}
          </div>
          {experience?.quote ? <blockquote>“{experience.quote}”</blockquote> : null}
          {synopsis ? (
            <div className={styles.synopsis}>
              <p>{visibleSynopsis}</p>
              {shouldCollapse ? <button type="button" onClick={onToggleSynopsis}>{expandedSynopsis ? "Less" : "More"}</button> : null}
            </div>
          ) : null}
          {experience?.writers?.length ? (
            <p className={styles.writers}><span>Written / Created by</span> {(experience.writers ?? []).join(", ")}</p>
          ) : null}
          <div className={styles.heroActions}>
            {experience?.trailer ? (
              <button type="button" className={styles.primaryAction} onClick={() => onTrailer(experience.trailer!)}>
                ▶ Watch Trailer
              </button>
            ) : null}
            <a
                className={styles.secondaryAction}
                href={futurePath(hero)}
              >
                More Info
              </a>
            <button type="button" className={styles.secondaryAction} aria-disabled="true" disabled>＋ My List</button>
          </div>
        </div>
      </div>
    </section>
  );
}

function SectionHeading({
  title,
  note,
  destination,
}: {
  title: string;
  note?: string;
  destination?: string;
}) {
  return (
    <div className={styles.sectionHeading}>
      <div>
        <h2>{title}</h2>
        {note ? <p>{note}</p> : null}
      </div>
      {destination ? (
        <a href={destination} className={styles.seeAll}>
          See All →
        </a>
      ) : null}
    </div>
  );
}

function ContentRail({ title, items }: { title: string; items: HomeItem[] }) {
  if (!items.length) return null;
  return (
    <section className={styles.section}>
      <SectionHeading
        title={title}
        destination={`/discover/${title
          .toLocaleLowerCase()
          .replace(/[^a-z0-9]+/g, "-")
          .replace(/^-|-$/g, "")}`}
      />
      <div className={styles.rail}>
        {items.map((item) => <MediaCard key={`${item.media_type}-${item.provider_id}`} item={item} />)}
      </div>
    </section>
  );
}

function MediaCard({ item }: { item: HomeItem }) {
  const art = item.backdrop_url ?? item.poster_url;
  return (
    <a
      href={futurePath(item)}
      className={styles.card}
      data-provider-id={item.provider_id}
      data-media-type={item.media_type}
      data-genre-ids={(item.genre_ids ?? []).join(",")}
      aria-label={`${item.title}. Future details destination preserved.`}
    >
      <div className={styles.cardArt}>
        {art ? <img src={art} alt="" loading="lazy" /> : <div className={styles.noArt}>C</div>}
        {item.rating ? <span className={styles.cardScore}>{item.rating.value.toFixed(1)}</span> : null}
      </div>
      <strong>{item.title}</strong>
      <small>{yearFromDate(item.date) ?? mediaLabel(item)}</small>
    </a>
  );
}

function LazyRail({ slug }: { slug: string }) {
  const ref = useRef<HTMLElement | null>(null);
  const [payload, setPayload] = useState<HomeRailResponse | null>(null);
  const [started, setStarted] = useState(false);

  useEffect(() => {
    const node = ref.current;
    if (!node || started) return;
    const observer = new IntersectionObserver((entries) => {
      if (!entries.some((entry) => entry.isIntersecting)) return;
      setStarted(true);
      observer.disconnect();
      fetch(`/api/cinewatch/home/rails/${slug}`, { cache: "no-store" })
        .then((response) => (response.ok ? response.json() : null))
        .then((value) => setPayload(value))
        .catch(() => setPayload(null));
    }, { rootMargin: "700px 0px" });
    observer.observe(node);
    return () => observer.disconnect();
  }, [slug, started]);

  return (
    <section ref={ref} className={styles.section} data-lazy-rail={slug}>
      {payload?.items?.length ? (
        <>
          <SectionHeading title={payload.title} />
          <div className={styles.rail}>
            {payload.items.map((item) => <MediaCard key={`${item.media_type}-${item.provider_id}`} item={item} />)}
          </div>
        </>
      ) : started ? null : <CompactLoading />}
    </section>
  );
}

function CompactLoading() {
  return <RailSkeleton />;
}

function RailSkeleton() {
  return (
    <div className={styles.skeletonWrap} aria-hidden="true">
      <div className={styles.skeletonTitle} />
      <div className={styles.skeletonRail}>{Array.from({ length: 6 }, (_, index) => <span key={index} />)}</div>
    </div>
  );
}

function LazyGenres() {
  const ref = useRef<HTMLElement | null>(null);
  const [genres, setGenres] = useState<HomeGenreEntry[]>([]);
  const [started, setStarted] = useState(false);

  useEffect(() => {
    const node = ref.current;
    if (!node || started) return;
    const observer = new IntersectionObserver((entries) => {
      if (!entries.some((entry) => entry.isIntersecting)) return;
      setStarted(true);
      observer.disconnect();
      fetch("/api/cinewatch/home/genres", { cache: "no-store" })
        .then((response) => (response.ok ? response.json() as Promise<HomeGenresResponse> : null))
        .then((payload) => setGenres(payload?.genres ?? []))
        .catch(() => setGenres([]));
    }, { rootMargin: "700px 0px" });
    observer.observe(node);
    return () => observer.disconnect();
  }, [started]);

  return (
    <section ref={ref} className={styles.section}>
      {genres.length ? (
        <>
          <SectionHeading
          title="Genres"
          destination="/genres"
        />
          <div className={styles.genreGrid}>
            {genres.map((genre) => (
              <a key={genre.slug} href={genre.future_path}>
                <span>{genre.name}</span>
              </a>
            ))}
          </div>
        </>
      ) : started ? null : <RailSkeleton />}
    </section>
  );
}

function LazyTrailerRail({ onTrailer }: { onTrailer: (title: string, trailer: HomeTrailer) => void }) {
  const ref = useRef<HTMLElement | null>(null);
  const [payload, setPayload] = useState<HomeTrailerRailResponse | null>(null);
  const [started, setStarted] = useState(false);

  useEffect(() => {
    const node = ref.current;
    if (!node || started) return;
    const observer = new IntersectionObserver((entries) => {
      if (!entries.some((entry) => entry.isIntersecting)) return;
      setStarted(true);
      observer.disconnect();
      fetch("/api/cinewatch/home/trailers", { cache: "no-store" })
        .then((response) => (response.ok ? response.json() : null))
        .then((value) => setPayload(value))
        .catch(() => setPayload(null));
    }, { rootMargin: "700px 0px" });
    observer.observe(node);
    return () => observer.disconnect();
  }, [started]);

  return (
    <section ref={ref} className={styles.section}>
      {payload?.items?.length ? (
        <>
          <SectionHeading title={payload.title} />
          <div className={styles.trailerRail}>
            {payload.items.map(({ item, trailer }) => {
              const art = item.backdrop_url ?? item.poster_url;
              return (
                <button key={`${item.provider_id}-${trailer.youtube_key}`} type="button" onClick={() => onTrailer(item.title, trailer)} className={styles.trailerCard}>
                  {art ? <img src={art} alt="" loading="lazy" /> : null}
                  <span className={styles.playDisc}>▶</span>
                  <strong>{item.title}</strong>
                  <small>{trailer.video_type}</small>
                </button>
              );
            })}
          </div>
        </>
      ) : started ? null : <RailSkeleton />}
    </section>
  );
}

function TrailerModal({ title, trailer, onClose }: { title: string; trailer: HomeTrailer; onClose: () => void }) {
  useEffect(() => {
    function keydown(event: KeyboardEvent) {
      if (event.key === "Escape") onClose();
    }
    window.addEventListener("keydown", keydown);
    return () => window.removeEventListener("keydown", keydown);
  }, [onClose]);

  return (
    <div className={styles.modalBackdrop} role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget) onClose(); }}>
      <section className={styles.modal} role="dialog" aria-modal="true" aria-label={`Trailer for ${title}`}>
        <div className={styles.modalHeader}>
          <div><strong>{title}</strong><small>{trailer.name}</small></div>
          <button type="button" onClick={onClose} aria-label="Close trailer">×</button>
        </div>
        <div className={styles.videoFrame}>
          <iframe
            src={`https://www.youtube-nocookie.com/embed/${encodeURIComponent(trailer.youtube_key)}?autoplay=1&rel=0`}
            title={`${title} trailer`}
            allow="autoplay; encrypted-media; picture-in-picture"
            allowFullScreen
          />
        </div>
      </section>
    </div>
  );
}
