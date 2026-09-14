import type { CatalogReviewsResponse } from "@cinewatch/contracts";
import Link from "next/link";

import { RatingSourceLogo } from "./MediaIdentity";
import styles from "./ReviewsPage.module.css";

export default function ReviewsPage({ payload, titlePath }: { payload: CatalogReviewsResponse; titlePath: string }) {
  return (
    <main className={styles.page}>
      <Link href={titlePath}>← Back to title</Link>
      <div className={styles.sourceHeading}><RatingSourceLogo source="tmdb" /><span>Reviews</span></div>
      <h1>Reviews</h1>
      <p>{payload.total_results.toLocaleString()} reviews</p>
      <div className={styles.list}>{(payload.reviews ?? []).map((review) => <article key={review.provider_review_id}><header><strong>{review.author}</strong>{review.rating != null ? <span>{review.rating.toFixed(1)}/10</span> : null}</header><p>{review.content}</p><small className={styles.sourceMark}><RatingSourceLogo source="tmdb" /></small></article>)}</div>
      <nav>{payload.page > 1 ? <Link href={`${titlePath}/reviews?page=${payload.page - 1}`}>← Previous</Link> : null}{payload.page < payload.total_pages ? <Link href={`${titlePath}/reviews?page=${payload.page + 1}`}>Next →</Link> : null}</nav>
    </main>
  );
}
