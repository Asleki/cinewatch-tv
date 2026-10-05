/* eslint-disable @next/next/no-img-element */

import styles from "./MediaIdentity.module.css";

export type RatingSource = "tmdb" | "imdb" | "rotten_tomatoes" | "metacritic";

const logos: Record<RatingSource, { src: string; alt: string }> = {
  imdb: { src: "/brand/ratings/imdb.jpg", alt: "IMDb" },
  rotten_tomatoes: { src: "/brand/ratings/rotten-tomatoes.jpg", alt: "Rotten Tomatoes" },
  metacritic: { src: "/brand/ratings/metacritic.jpg", alt: "Metacritic" },
  tmdb: { src: "/brand/ratings/tmdb.jpg", alt: "TMDb" },
};

export function RatingSourceLogo({ source }: { source: string }) {
  const logo = logos[source as RatingSource];
  if (!logo) return <span className={styles.ratingText}>{source}</span>;
  return <span className={styles.ratingLogoFrame}><img className={styles.ratingLogo} src={logo.src} alt={logo.alt} title={logo.alt} /></span>;
}

export function MediaTypeIcon({ mediaType, withLabel = false }: { mediaType: "movie" | "tv"; withLabel?: boolean }) {
  const common = { width: 16, height: 16, viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: 1.8, strokeLinecap: "round" as const, strokeLinejoin: "round" as const, "aria-hidden": true };
  const icon = mediaType === "tv"
    ? <svg {...common}><rect x="3" y="6" width="18" height="13" rx="2" /><path d="m8 3 4 3 4-3" /></svg>
    : <svg {...common}><rect x="3" y="4" width="18" height="16" rx="2" /><path d="M7 4v16M17 4v16M3 9h4M17 9h4M3 15h4M17 15h4" /></svg>;
  return <span className={styles.mediaType}>{icon}{withLabel ? <span>{mediaType === "tv" ? "TV" : "Movie"}</span> : null}</span>;
}
