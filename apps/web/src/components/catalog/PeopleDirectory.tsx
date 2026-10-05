"use client";
/* eslint-disable @next/next/no-img-element */
import Link from "next/link";
import { useState } from "react";
import styles from "./PeopleDirectory.module.css";

type Person = { provider_id: number; name: string; profile_url: string | null; known_for_department: string | null; future_path: string };
type Response = { page: number; total_pages: number; department: string | null; items: Person[] };
const departments = ["", "Acting", "Writing", "Directing", "Production"];

export default function PeopleDirectory({ initial }: { initial: Response | null }) {
  const [payload, setPayload] = useState(initial);
  const [people, setPeople] = useState<Person[]>(initial?.items ?? []);
  const [department, setDepartment] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(false);

  async function load(page: number, chosen = department) {
    setBusy(true); setError(false);
    try {
      const params = new URLSearchParams({ page: String(page) });
      if (chosen) params.set("department", chosen);
      const response = await fetch(`/api/cinewatch/directory/people?${params}`, { cache: "no-store" });
      if (!response.ok) throw new Error("People unavailable");
      const next = await response.json() as Response;
      setPayload(next);
      setPeople((current) => page === 1 ? next.items : [...current, ...next.items.filter((item) => !current.some((old) => old.provider_id === item.provider_id))]);
    } catch { setError(true); }
    finally { setBusy(false); }
  }
  return <main className={styles.page}>
    <p className={styles.eyebrow}>Discover</p><h1>People</h1>
    <div className={styles.filters} aria-label="Known for department">
      {departments.map((option) => <button type="button" key={option} aria-pressed={department === option} onClick={() => { setDepartment(option); void load(1, option); }}>{option || "All"}</button>)}
    </div>
    <div className={styles.grid}>{people.map((person) => <Link href={person.future_path} className={styles.card} key={person.provider_id}>
      <span>{person.profile_url ? <img src={person.profile_url} alt="" loading="lazy" /> : <b>C</b>}</span><strong>{person.name}</strong>
    </Link>)}</div>
    {error ? <div className={styles.status}>People could not be loaded. <button type="button" onClick={() => void load(payload?.page ?? 1)}>Retry</button></div> : null}
    {!people.length && !busy && !error ? <p>No people found for this department on this results page.</p> : null}
    {payload && payload.page < payload.total_pages ? <div className={styles.more}><button type="button" disabled={busy} onClick={() => void load(payload.page + 1)}>{busy ? "Loading…" : "Load more people"}</button></div> : null}
  </main>;
}
