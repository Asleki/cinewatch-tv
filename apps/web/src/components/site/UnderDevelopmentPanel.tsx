"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";

import styles from "@/app/r3-page.module.css";

const descriptions: Record<string, { title: string; reason: string }> = {
  "cinema-guide": { title: "Cinema Guide is under development", reason: "Cinema and showtime information is not ready for live use yet." },
  "music-tracks": { title: "Music & Tracks is under development", reason: "Music connected to titles is not ready for live use yet. CineWatch will not guess which song belongs to a film or episode." },
  "account": { title: "Account is under development", reason: "Account features are still being prepared." },
  "my-list": { title: "My List is under development", reason: "Saving titles to My List is still being prepared." },
};

function humanize(value: string): string {
  return value.replace(/-/g, " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

export default function UnderDevelopmentPanel({ feature }: { feature: string }) {
  const router = useRouter();
  const known = descriptions[feature];
  const title = known?.title ?? `${humanize(feature)} is under development`;
  const reason = known?.reason ?? "This part of CineWatch is still being prepared for live use.";
  return (
    <main className={styles.page}>
      <section className={styles.hero}>
        <span className={styles.chip}>Under Development</span>
        <p className={styles.eyebrow}>CineWatch TV</p>
        <h1>{title}</h1>
        <p>{reason}</p>
        {feature === "privacy" && <p>You can return to the homepage using the Home button below.</p>}
        <div className={styles.actions}>
          <button type="button" className={styles.buttonSecondary} onClick={() => router.back()}>← Back</button>
          <Link className={styles.button} href="/">Home</Link>
        </div>
      </section>
    </main>
  );
}
