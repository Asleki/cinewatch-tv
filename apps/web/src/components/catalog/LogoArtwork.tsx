"use client";
/* eslint-disable @next/next/no-img-element */
import { useState } from "react";
import { getLogoMatte } from "@/lib/presentation/logo-matte";
import styles from "./LogoArtwork.module.css";

export default function LogoArtwork({ src, name }: { src: string | null; name: string }) {
  const [failedSrc, setFailedSrc] = useState<string | null>(null);
  const available = src !== null && failedSrc !== src;
  return <span className={styles.frame} data-logo-matte={available ? getLogoMatte(src) : "missing"}>
    {available ? <img src={src} alt={`${name} logo`} onError={() => setFailedSrc(src)} /> :
      <span className={styles.fallback} role="img" aria-label={`${name} logo unavailable`}>C</span>}
  </span>;
}
