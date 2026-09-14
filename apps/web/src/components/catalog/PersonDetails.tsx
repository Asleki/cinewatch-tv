/* eslint-disable @next/next/no-img-element */

import type { CatalogPersonResponse } from "@cinewatch/contracts";
import Link from "next/link";

import styles from "./PersonDetails.module.css";

export default function PersonDetails({ person }: { person: CatalogPersonResponse }) {
  return (
    <main>
      <section className={styles.hero} style={person.hero_backdrop_url ? { backgroundImage: `url(${person.hero_backdrop_url})` } : undefined}>
        <div className={styles.shade} />
        <div className={styles.inner}>
          {person.profile_url ? <img src={person.profile_url} alt={`${person.name} profile`} /> : <span className={styles.profileFallback}>C</span>}
          <div><p>Person</p><h1>{person.name}</h1>{person.known_for_department ? <strong>{person.known_for_department}</strong> : null}<div className={styles.meta}>{person.birthday ? <span>Born {person.birthday}</span> : null}{person.place_of_birth ? <span>{person.place_of_birth}</span> : null}</div></div>
        </div>
      </section>
      <div className={styles.body}>
        <section><h2>Biography</h2><p className={styles.biography}>{person.biography || "Biography is not available from the current provider."}</p></section>
        <section><h2>Filmography & Roles</h2><div className={styles.credits}>{(person.credits ?? []).map((credit) => <Link key={`${credit.media_type}-${credit.provider_id}`} href={credit.future_path}>{credit.poster_url ? <img src={credit.poster_url} alt="" loading="lazy" /> : <span>C</span>}<div><strong>{credit.title}</strong><small>{credit.role || "Role unavailable"}{credit.year ? ` · ${credit.year}` : ""}</small></div></Link>)}</div></section>
      </div>
    </main>
  );
}
