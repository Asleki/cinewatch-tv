/* eslint-disable @next/next/no-img-element */
"use client";
import { useEffect,useState,useRef,useCallback } from "react";
import Link from "next/link";
import { CineWatchPlayer } from "@/components/player/CineWatchPlayer";
import { RatingSourceLogo } from "@/components/catalog/MediaIdentity";
import type { PlayableManifest } from "@/lib/playable/types";
import { assertPlayableManifest } from "@/lib/playable/validate";
import styles from "./WatchExperience.module.css";
export type EpisodeCard={id:string;number:number;name:string;still:string|null;overview:string|null;available:boolean};
export type WatchDetails={title:string;seasonName:string;year:string|null;country:string|null;ratings:{source:string;display_value:string}[];detailsPath:string;poster:string|null;backdrop:string|null;primaryTrailer:string;episodes:EpisodeCard[]};
export default function WatchExperience({details}:{details:WatchDetails}) {
 const [manifest,setManifest]=useState<PlayableManifest|null>(null);
 const [selected,setSelected]=useState(details.primaryTrailer);
 const [message,setMessage]=useState("Preparing your player…");
 const [loading,setLoading]=useState(false);
 const requestId=useRef(0);
 const select=useCallback(async (id:string) => {
  const version=++requestId.current;setLoading(true);setMessage("Loading…");
  try {const response=await fetch(`/api/cinewatch/watch/manifest/${id}`,{cache:"no-store"});
   if(!response.ok)throw new Error(response.status===401?"Sign in to watch":"This video is unavailable");
   const next=assertPlayableManifest(await response.json());if(version!==requestId.current)return;
   setManifest(next);setSelected(id);setMessage("");
  }catch(e){if(version===requestId.current){setManifest(null);setMessage(e instanceof Error?e.message:"Playback unavailable");}}
  finally{if(version===requestId.current)setLoading(false);}
 },[]);
 useEffect(()=>{let cancelled=false;const sequence=requestId;queueMicrotask(()=>{if(!cancelled)void select(details.primaryTrailer);});return()=>{cancelled=true;sequence.current++;};},[details.primaryTrailer,select]);
 const active=details.episodes.find(e=>e.id===selected);
 return <section className={styles.watch} aria-label="CineWatch watch page" style={details.backdrop?{"--watch-backdrop":`url("${details.backdrop}")`} as React.CSSProperties:undefined}>
  <div className={styles.stage}>
   {manifest?<CineWatchPlayer manifest={manifest} autoPlay initiallyMuted={!active}/>:<div className={styles.signIn}>
    {details.poster?<img src={details.poster} alt="" className={styles.poster}/>:null}
    <h1>{details.title} · {details.seasonName}</h1><p role="status">{message}</p>
    {!loading?<a className={styles.action} href="/api/cinewatch/watch/sign-in">Sign in to watch</a>:null}
   </div>}
  </div>
  <div className={styles.identity}>
   <div><p className={styles.eyebrow}>{details.seasonName}</p><h1>{details.title}</h1><p aria-live="polite">{active?`${active.id} · ${active.name}`:"Season 2 Volume Two · Preview"}</p>
    <div className={styles.metadata}>{details.ratings.map(r=><span className={styles.rating} key={r.source}><RatingSourceLogo source={r.source}/>{r.display_value}</span>)}{details.country?<span>{details.country}</span>:null}{details.year?<span>{details.year}</span>:null}</div>
   </div><Link href={details.detailsPath} className={styles.action}>View Details</Link>
  </div>
  <div className={styles.sectionHeading}><h2>Episodes</h2><p>Choose an episode to watch here.</p></div>
  <div className={styles.episodes}>{details.episodes.map(e=><button key={e.id} type="button" className={`${styles.episode} ${selected===e.id?styles.selected:""}`} disabled={!e.available||loading} aria-pressed={selected===e.id} onClick={()=>void select(e.id)}>
   <span className={styles.image}>{e.still?<img src={e.still} alt="" loading="lazy"/>:<span>{details.title}</span>}<span className={styles.ordinal}>{e.number.toString().padStart(2,"0")}</span></span>
   <span className={styles.cardText}><span className={styles.eyebrow}>{e.id}</span><strong>{e.name}</strong>{e.overview?<span className={styles.overview}>{e.overview}</span>:null}<span className={styles.cardAction}>{!e.available?"Unavailable":selected===e.id?"Selected":"Watch episode"}</span></span>
  </button>)}</div>
  {loading&&manifest?<p role="status">Loading selected video…</p>:null}
 </section>;
}
