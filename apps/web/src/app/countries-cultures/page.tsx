/* eslint-disable @next/next/no-img-element */
import Link from "next/link";
import { getPublicApiBaseUrl } from "@/lib/config/public-env";
import styles from "./page.module.css";

export const dynamic = "force-dynamic";

const countries = [
  ["KE", "Kenya"], ["NG", "Nigeria"], ["IN", "India"],
  ["KR", "South Korea"], ["CN", "China"], ["US", "United States"],
  ["GB", "United Kingdom"], ["ZA", "South Africa"], ["GH", "Ghana"],
] as const;

type Browse = { items: { poster_url: string | null; backdrop_url: string | null }[] };
async function countryArtwork(code: string): Promise<string | null> {
  try {
    const url = new URL(`/api/v1/catalog/browse/country/${code}?media_type=movie`, getPublicApiBaseUrl());
    const response = await fetch(url, { next: { revalidate: 3600 } });
    if (!response.ok) return null;
    const payload = await response.json() as Browse;
    return payload.items.find((item) => item.poster_url)?.poster_url ?? null;
  } catch { return null; }
}

export default async function CountriesCulturesPage() {
  const artwork = await Promise.all(countries.map(([code]) => countryArtwork(code)));
  return <main className={styles.page}>
    <p className={styles.eyebrow}>Discover</p><h1>Countries & Cultures</h1>
    <p className={styles.intro}>Explore films and series by country of origin. Language and genre can take you further into each collection.</p>
    <div className={styles.grid}>{countries.map(([code, name], index) => <Link className={styles.card} href={`/country/${code.toLowerCase()}`} key={code}>
      <span className={styles.art}>{artwork[index] ? <img src={artwork[index]} alt="" loading="lazy" /> : <b aria-hidden="true">C</b>}</span>
      <strong>Stories from {name}</strong>
    </Link>)}</div>
  </main>;
}
