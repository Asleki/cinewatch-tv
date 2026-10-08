/* eslint-disable @next/next/no-img-element */
import styles from "./StreamNowAnimation.module.css";

export default function StreamNowAnimation() {
  return (
    <section className={styles.scene} aria-label="CineWatch TV">
      <div className={styles.atmosphere} aria-hidden="true">
        <span className={styles.ribbon} />
        <span className={styles.ribbon} />
        <span className={styles.ribbon} />
        <span className={styles.halo} />
      </div>
      <img className={styles.mark} src="/brand/cinewatch-mark-r1a-full.svg" alt="CineWatch TV" />
    </section>
  );
}
