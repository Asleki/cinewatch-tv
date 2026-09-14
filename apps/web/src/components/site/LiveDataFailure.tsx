import Link from "next/link";

import styles from "@/app/r3-page.module.css";

export default function LiveDataFailure({ title, message }: { title: string; message: string }) {
  return (
    <main className={styles.page}>
      <section className={styles.hero}>
        <span className={styles.chip}>Unavailable</span>
        <p className={styles.eyebrow}>CineWatch TV</p>
        <h1>{title}</h1>
        <p>{message}</p>
        <div className={styles.actions}><Link className={styles.buttonSecondary} href="/">Home</Link></div>
      </section>
    </main>
  );
}
