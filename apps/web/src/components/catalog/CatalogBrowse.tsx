import type { CatalogBrowseResponse } from "@cinewatch/contracts";
import Link from "next/link";

import CatalogCard from "./CatalogCard";
import shared from "./CatalogShared.module.css";
import styles from "./CatalogBrowse.module.css";

type Props = {
  payload: CatalogBrowseResponse;
  basePath: string;
  genreOptions?: { slug: string; name: string }[];
};

function pageHref(basePath: string, payload: CatalogBrowseResponse, page: number) {
  const params = new URLSearchParams();
  params.set("page", String(page));
  if (payload.media_type !== "all") params.set("media_type", payload.media_type);
  if (payload.year) params.set("year", String(payload.year));
  if (payload.language) params.set("language", payload.language);
  if (payload.genre) params.set("genre", payload.genre);
  if (payload.sort !== "popularity.desc") params.set("sort", payload.sort);
  return `${basePath}?${params.toString()}`;
}

export default function CatalogBrowse({ payload, basePath, genreOptions = [] }: Props) {
  return (
    <main className={shared.page}>
      <p className={shared.eyebrow}>Discover</p>
      <h1>{payload.title}</h1>

      <form className={styles.filters} method="get" action={basePath}>
        <label>Type
          <select name="media_type" defaultValue={payload.media_type}>
            <option value="all">Movies & TV</option>
            <option value="movie">Movies</option>
            <option value="tv">TV Shows</option>
          </select>
        </label>
        <label>Year
          <input name="year" inputMode="numeric" pattern="[0-9]{4}" defaultValue={payload.year ?? ""} placeholder="Any year" />
        </label>
        <label>Preferred language
          <select name="language" defaultValue={payload.language ?? ""}>
            <option value="">Any language</option>
            <option value="en">English</option>
            <option value="sw">Swahili</option>
            <option value="ko">Korean</option>
            <option value="hi">Hindi</option>
            <option value="te">Telugu</option>
            <option value="pa">Punjabi</option>
            <option value="ta">Tamil</option>
            <option value="zh">Chinese</option>
            <option value="yo">Yoruba</option>
          </select>
        </label>
        {genreOptions.length ? <label>Genre
          <select name="genre" defaultValue={payload.genre ?? ""}><option value="">Any genre</option>{genreOptions.map((item) => <option value={item.slug} key={item.slug}>{item.name}</option>)}</select>
        </label> : null}
        <label>Sort
          <select name="sort" defaultValue={payload.sort}>
            <option value="popularity.desc">Most popular</option>
            <option value="vote_average.desc">Highest rated</option>
            <option value="primary_release_date.desc">Newest movies</option>
            <option value="first_air_date.desc">Newest TV</option>
          </select>
        </label>
        <button type="submit">Apply filters</button>
      </form>

      {(payload.items ?? []).length ? (
        <div className={shared.grid}>{(payload.items ?? []).map((item) => <CatalogCard key={`${item.media_type}-${item.provider_id}`} item={item} />)}</div>
      ) : (
        <section className={shared.empty}><div><h2>No matching titles yet</h2><p>Try widening the filters for this CineWatch collection.</p></div></section>
      )}

      <nav className={shared.pager} aria-label="Browse pages">
        {payload.page > 1 ? <Link className={shared.buttonLink} href={pageHref(basePath, payload, payload.page - 1)}>← Previous</Link> : null}
        {payload.page < payload.total_pages ? <Link className={shared.buttonLink} href={pageHref(basePath, payload, payload.page + 1)}>Next →</Link> : null}
      </nav>
    </main>
  );
}
