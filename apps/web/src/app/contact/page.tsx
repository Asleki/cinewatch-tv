import styles from "@/app/r3-page.module.css";

export default function ContactPage() {
  return (
    <main className={styles.page}>
      <section className={styles.hero}>
        <p className={styles.eyebrow}>Contact CineWatch TV</p>
        <h1>Talk to CineWatch.</h1>
        <p>Reach CineWatch TV by email or through our Facebook page.</p>
      </section>
      <section className={styles.contactGrid} aria-label="Contact methods">
        <a className={styles.contactCard} href="mailto:cinewatchtv.stream@gmail.com">
          <span>Email</span>
          <strong>cinewatchtv.stream@gmail.com</strong>
          <p className={styles.muted}>Questions, feedback and CineWatch enquiries.</p>
        </a>
        <a className={styles.contactCard} href="https://www.facebook.com/share/1DVjk2QY9s/" target="_blank" rel="noopener noreferrer">
          <span>Facebook</span>
          <strong>CineWatch TV</strong>
          <p className={styles.muted}>Open the approved CineWatch TV Facebook destination.</p>
        </a>
      </section>
    </main>
  );
}
