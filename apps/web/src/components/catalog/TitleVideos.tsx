"use client";
/* eslint-disable @next/next/no-img-element */

import Link from "next/link";
import { useState } from "react";

import styles from "./TitleVideos.module.css";

type Video = {
  youtube_key: string;
  name: string;
  video_type: "Trailer" | "Teaser" | "Clip" | "Featurette" | "Behind the Scenes";
  official: boolean;
  published_at: string | null;
  season_number: number | null;
};

export default function TitleVideos({ title, mediaType, providerId, videos }: { title: string; mediaType: "movie" | "tv"; providerId: number; videos: Video[] }) {
  const [selected, setSelected] = useState<Video | null>(videos[0] ?? null);
  return (
    <main className={styles.page}>
      <Link className={styles.back} href={`/title/${mediaType}/${providerId}`}>← Back to {title}</Link>
      <p className={styles.eyebrow}>YouTube · Trailers & Teasers</p>
      <h1>Trailers & Teasers</h1>
      <p className={styles.intro}>Choose a trailer, teaser, clip or featurette.</p>
      {!selected ? <div className={styles.empty}><strong>No video is available for this title.</strong><span>Try another title or return later.</span></div> : <>
        <section className={styles.player}>
          <iframe src={`https://www.youtube-nocookie.com/embed/${encodeURIComponent(selected.youtube_key)}?rel=0`} title={`${title}: ${selected.name}`} allow="encrypted-media; picture-in-picture; fullscreen" allowFullScreen />
          <div><span>YouTube</span><strong>{selected.name}</strong><small>{selected.video_type}{selected.official ? " · Official" : ""}{selected.season_number != null ? ` · Season ${selected.season_number}` : ""}</small></div>
        </section>
        <section className={styles.grid} aria-label={`${title} videos`}>
          {videos.map((video) => <button type="button" key={`${video.youtube_key}-${video.video_type}`} onClick={() => setSelected(video)} className={selected.youtube_key === video.youtube_key ? styles.selected : undefined}><img src={`https://i.ytimg.com/vi/${encodeURIComponent(video.youtube_key)}/hqdefault.jpg`} alt="" loading="lazy" /><span><strong>{video.name}</strong><small>YouTube · {video.video_type}{video.official ? " · Official" : ""}</small></span></button>)}
        </section>
      </>}
    </main>
  );
}
