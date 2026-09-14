/* eslint-disable @next/next/no-img-element */

import type { CatalogPersonResponse } from "@cinewatch/contracts";
import Link from "next/link";

import RelatedNews from "@/components/news/RelatedNews";

import styles from "./PersonDetails.module.css";

type PersonCredit = NonNullable<CatalogPersonResponse["credits"]>[number];
type ExtendedPerson = CatalogPersonResponse & { crew_credits?: PersonCredit[] };

function CreditGrid({ credits }: { credits: PersonCredit[] }) {
  return <div className={styles.credits}>{credits.map((credit) => <Link key={`${credit.media_type}-${credit.provider_id}-${credit.role ?? "credit"}`} href={credit.future_path}>{credit.poster_url ? <img src={credit.poster_url} alt="" loading="lazy" /> : <span>C</span>}<div><strong>{credit.title}</strong><small>{credit.role || "Role unavailable"}{credit.year ? ` · ${credit.year}` : ""}</small></div></Link>)}</div>;
}

export default function PersonDetails({ person }: { person: ExtendedPerson }) {
  const credits = person.credits ?? [];
  const crew = person.crew_credits ?? [];
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
        <section><h2>Biography</h2><p className={styles.biography}>{person.biography || "Biography is not available."}</p></section>
        <section><h2>Filmography & Acting Roles</h2>{credits.length ? <CreditGrid credits={credits} /> : <p className={styles.biography}>No acting credits are available.</p>}</section>
        {crew.length ? <section><h2>Behind the Camera</h2><CreditGrid credits={crew} /></section> : null}
        <RelatedNews query={person.name} heading={`${person.name} in the News`} />
      </div>
    </main>
  );
}
