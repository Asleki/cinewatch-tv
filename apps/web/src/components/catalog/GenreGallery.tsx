"use client";
import type { HomeGenreEntry } from "@cinewatch/contracts";
import { useState } from "react";
import GenreCard from "./GenreCard";
import styles from "./GenreGallery.module.css";

export default function GenreGallery({ genres }: { genres: HomeGenreEntry[] }) {
  const [visible, setVisible] = useState(12);
  return <>
    <div className={styles.grid}>{genres.slice(0, visible).map((genre) => <GenreCard key={genre.slug} genre={genre} />)}</div>
    {visible < genres.length ? <div className={styles.more}><button type="button" onClick={() => setVisible((current) => Math.min(current + 12, genres.length))}>Load more genres</button></div> : null}
  </>;
}
