/* eslint-disable @next/next/no-img-element */
import type { HomeGenreEntry } from "@cinewatch/contracts";
import Link from "next/link";
import styles from "./GenreCard.module.css";

export default function GenreCard({ genre }: { genre: HomeGenreEntry }) {
  return <Link className={styles.card} href={genre.future_path}>
    <span className={styles.art}>{genre.poster_url ? <img src={genre.poster_url} alt="" loading="lazy" /> : <span className={styles.fallback} aria-hidden="true">C</span>}</span>
    <strong>{genre.name}</strong>
  </Link>;
}
