import "server-only";
import { getPublicApiBaseUrl } from "@/lib/config/public-env";
import { loadCatalogTitle } from "@/lib/api/catalog-client";
import { BONANZA } from "./catalog";
import type { WatchDetails } from "@/components/watch/WatchExperience";
import originals from "./registry.json";
type Season={name:string;poster_url:string|null;episodes:{episode_number:number;name:string;still_url:string|null;overview:string|null;air_date:string|null}[]};
export async function watchMetadata():Promise<WatchDetails|null> {
 try {
  const title=await loadCatalogTitle("tv",BONANZA.providerId);if(!title)return null;
  const response=await fetch(new URL(`/api/v1/catalog/title/tv/${BONANZA.providerId}/season/2`,getPublicApiBaseUrl()),{cache:"no-store"});
  if(!response.ok)return null;const season=await response.json() as Season;
  const countries=(title as typeof title & {origin_countries?:string[]}).origin_countries??[];
  const names=new Intl.DisplayNames(["en"],{type:"region"});
  return {title:title.title,seasonName:season.name,year:season.episodes.find(e=>e.air_date)?.air_date?.slice(0,4)??null,country:countries.length?countries.map(code=>names.of(code)??code).join(" · "):null,ratings:title.ratings??[],detailsPath:`/title/tv/${BONANZA.providerId}/details`,poster:season.poster_url??title.poster_url??null,backdrop:title.backdrop_url??null,primaryTrailer:BONANZA.primaryTrailer,
    episodes:season.episodes.filter(e=>e.episode_number<=17).map(e=>{const id=`S02E${e.episode_number.toString().padStart(2,"0")}`;const source=originals[id as keyof typeof originals];return {id,number:e.episode_number,name:e.name,still:e.still_url,overview:e.overview,available:!!source?.available};})};
 } catch { return null; }
}
