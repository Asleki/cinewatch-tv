
import type { HomeGenresResponse } from "@cinewatch/contracts";
import Link from "next/link";

import { getPublicApiBaseUrl } from "@/lib/config/public-env";

async function loadGenres(): Promise<HomeGenresResponse | null> {
  try {
    const response = await fetch(new URL("/api/v1/home/genres", getPublicApiBaseUrl()), { cache: "no-store" });
    return response.ok ? await response.json() as HomeGenresResponse : null;
  } catch { return null; }
}

export default async function GenresPage() {
  const payload = await loadGenres();
  return <main style={{width:"min(1100px,100%)",margin:"0 auto",padding:"42px clamp(16px,4vw,52px) 100px"}}><p style={{color:"var(--cw-aqua)",fontWeight:800}}>DISCOVER</p><h1 style={{fontSize:"clamp(2.5rem,7vw,5rem)",margin:"0 0 26px",letterSpacing:"-.05em"}}>Genres</h1><div style={{display:"grid",gridTemplateColumns:"repeat(auto-fit,minmax(150px,1fr))",gap:10}}>{payload?.genres?.map((genre) => <Link key={genre.slug} href={genre.future_path} style={{padding:"14px",border:"1px solid var(--cw-border)",borderRadius:10,background:"var(--cw-surface)",color:"var(--cw-text)",textDecoration:"none",fontWeight:750}}>{genre.name}</Link>)}</div></main>;
}
