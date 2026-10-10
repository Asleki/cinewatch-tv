/* eslint-disable @next/next/no-img-element */
import type { Metadata } from "next";
import Link from "next/link";
import { watchMetadata } from "@/lib/watch/metadata";
import { BONANZA } from "@/lib/watch/catalog";
import styles from "./page.module.css";
export const metadata:Metadata={title:"Stream Now"};
export const dynamic="force-dynamic";
export default async function StreamNowPage() {
 const details=await watchMetadata();
 return <section aria-label="Stream Now" className={styles.library}><h1>Stream Now</h1><p className={styles.intro}>Your next story starts here.</p>
  {details?<Link href={BONANZA.path} className={styles.card}>{details.poster?<img src={details.poster} alt={`${details.title} · ${details.seasonName}`} />:null}<span className={styles.caption}><span>{details.seasonName}</span><strong>{details.title}</strong><span>{details.year} · View episodes</span></span></Link>:<p>We couldn’t load this title. Please try again shortly.</p>}
 </section>;
}
