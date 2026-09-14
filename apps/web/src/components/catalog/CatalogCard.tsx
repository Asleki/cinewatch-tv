/* eslint-disable @next/next/no-img-element */

import type { CatalogMediaSummary } from "@cinewatch/contracts";
import Link from "next/link";

import styles from "./CatalogShared.module.css";

export default function CatalogCard({ item }: { item: CatalogMediaSummary }) {
  return (
    <Link className={styles.card} href={item.future_path}>
      <span className={styles.cardArt}>
        {item.poster_url ? <img src={item.poster_url} alt="" loading="lazy" /> : <span className={styles.noArt}>C</span>}
        {item.rating != null ? <b>{item.rating.toFixed(1)}</b> : null}
      </span>
      <strong>{item.title}</strong>
      <small>{item.year ?? "Year unavailable"} · {item.media_type === "tv" ? "TV" : "Movie"}</small>
    </Link>
  );
}
