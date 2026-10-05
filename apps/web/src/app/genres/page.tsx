
import type { HomeGenresResponse } from "@cinewatch/contracts";
import GenreGallery from "@/components/catalog/GenreGallery";

import { getPublicApiBaseUrl } from "@/lib/config/public-env";

async function loadGenres(): Promise<HomeGenresResponse | null> {
  try {
    const response = await fetch(new URL("/api/v1/home/genres", getPublicApiBaseUrl()), { cache: "no-store" });
    return response.ok ? await response.json() as HomeGenresResponse : null;
  } catch { return null; }
}

export default async function GenresPage() {
  const payload = await loadGenres();
  return <main style={{width:"min(1220px,100%)",margin:"0 auto",padding:"42px clamp(16px,4vw,52px) 120px"}}><p style={{color:"var(--cw-aqua)",fontWeight:800}}>DISCOVER</p><h1 style={{fontSize:"clamp(2.5rem,7vw,5rem)",margin:"0 0 26px",letterSpacing:"-.05em"}}>Genres</h1>{payload?.genres?.length ? <GenreGallery genres={payload.genres} /> : <p>Genres are temporarily unavailable.</p>}</main>;
}
