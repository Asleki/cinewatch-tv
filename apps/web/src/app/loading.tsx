import styles from "./loading.module.css";

export default function Loading() {
  return <div className={styles.loading} aria-busy="true" aria-label="Loading"><span className={styles.spinner} aria-hidden="true" /></div>;
}
