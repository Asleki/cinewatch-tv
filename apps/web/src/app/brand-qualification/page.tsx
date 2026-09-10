/* eslint-disable @next/next/no-img-element */
import type { Metadata } from "next";
import { notFound } from "next/navigation";

import styles from "./brand-qualification.module.css";

export const metadata: Metadata = {
  title: "Brand Qualification",
  description: "Local-only CineWatch TV production brand asset browser qualification.",
};

const microSizes = [16, 24, 32] as const;

export default function BrandQualificationPage() {
  if (process.env.NODE_ENV === "production") {
    notFound();
  }

  return (
    <main className={styles.page}>
      <header className={styles.header}>
        <div>
          <p className={styles.eyebrow}>CWTV.V1.3.2.3 · browser qualification</p>
          <h1>CineWatch TV production brand assets</h1>
          <p className={styles.lede}>
            Real files from <code>apps/web/public</code>. Human approval completed in this browser.
          </p>
        </div>
        <div className={styles.pending}>HUMAN APPROVED</div>
      </header>

      <section className={styles.grid}>
        <article className={styles.card}>
          <div className={styles.cardHead}>
            <h2>Primary lockup · light</h2><span>R1A · 64 px+</span>
          </div>
          <div className={styles.lockupStageLight}>
            <img className={styles.lockup} src="/brand/cinewatch-lockup-on-light.svg"
              alt="CineWatch TV lockup on light" />
          </div>
        </article>

        <article className={styles.card}>
          <div className={styles.cardHead}>
            <h2>Primary lockup · dark</h2><span>R1A · reversed</span>
          </div>
          <div className={styles.lockupStageDark}>
            <img className={styles.lockup} src="/brand/cinewatch-lockup-on-dark.svg"
              alt="CineWatch TV lockup on dark" />
          </div>
        </article>

        <article className={styles.card}>
          <div className={styles.cardHead}>
            <h2>Mark only</h2><span>Actual SVG files</span>
          </div>
          <div className={styles.markGrid}>
            <figure><div className={styles.squareLight}><img src="/brand/cinewatch-mark-r1a-full.svg" alt="R1A full color" /></div><figcaption>Full color</figcaption></figure>
            <figure><div className={styles.squareLight}><img src="/brand/cinewatch-mark-r1a-black.svg" alt="R1A black" /></div><figcaption>Black</figcaption></figure>
            <figure><div className={styles.squareDark}><img src="/brand/cinewatch-mark-r1a-white.svg" alt="R1A white" /></div><figcaption>White / reversed</figcaption></figure>
          </div>
        </article>

        <article className={styles.card}>
          <div className={styles.cardHead}>
            <h2>Wordmark only</h2><span>Outlined · no runtime font</span>
          </div>
          <div className={styles.wordmarkLight}><img src="/brand/cinewatch-wordmark-on-light.svg" alt="CineWatch TV wordmark on light" /></div>
          <div className={styles.wordmarkDark}><img src="/brand/cinewatch-wordmark-on-dark.svg" alt="CineWatch TV wordmark on dark" /></div>
        </article>

        <article className={styles.card}>
          <div className={styles.cardHead}>
            <h2>Native micro icons</h2><span>M1 · six-blade wide gap</span>
          </div>
          <p className={styles.note}>Native pixel sample first; pixelated enlargement is diagnostic only.</p>
          <div className={styles.microList}>
            <div className={styles.microRow}>
              <strong>Vector</strong>
              <span className={styles.nativeBox}>
                <img
                  src="/brand/cinewatch-mark-m1-full.svg"
                  width={32}
                  height={32}
                  alt="CineWatch TV M1 source vector"
                />
              </span>
              <span>Source vector · M1</span>
            </div>
            {microSizes.map((size) => (
              <div className={styles.microRow} key={size}>
                <strong>{size} px</strong>
                <span className={styles.nativeBox}>
                  <img src={`/icons/cinewatch-micro-${size}.png`} width={size} height={size}
                    alt={`M1 at ${size} pixels`} />
                </span>
                <div className={styles.zoomBox}>
                  <img src={`/icons/cinewatch-micro-${size}.png`} alt="" aria-hidden="true" />
                </div>
              </div>
            ))}
          </div>
        </article>

        <article className={styles.card}>
          <div className={styles.cardHead}>
            <h2>Browser favicon files</h2><span>Tab proof</span>
          </div>
          <div className={styles.iconGrid}>
            {[16, 32, 48].map((size) => (
              <figure key={size}>
                <div className={styles.faviconCell}>
                  <img src={`/icons/cinewatch-favicon-${size}.png`} width={size} height={size}
                    alt={`Favicon ${size} by ${size}`} />
                </div>
                <figcaption>{size} × {size}</figcaption>
              </figure>
            ))}
          </div>
          <p className={styles.note}>Also inspect the actual Chrome tab while this route is open.</p>
        </article>

        <article className={styles.card}>
          <div className={styles.cardHead}>
            <h2>Application icons</h2><span>Actual PNG exports</span>
          </div>
          <div className={styles.appGrid}>
            <figure>
              <img
                src="/icons/cinewatch-app-icon-180.png"
                alt="CineWatch TV 180 pixel app icon"
              />
              <figcaption>180 × 180</figcaption>
            </figure>
            <figure>
              <img
                src="/icons/cinewatch-app-icon-192.png"
                alt="CineWatch TV 192 pixel app icon"
              />
              <figcaption>192 × 192</figcaption>
            </figure>
            <figure>
              <img
                src="/icons/cinewatch-app-icon-512.png"
                alt="CineWatch TV 512 pixel app icon"
              />
              <figcaption>512 × 512</figcaption>
            </figure>
            <figure>
              <img src="/icons/cinewatch-app-icon-light-512.png" alt="Light app icon" />
              <figcaption>Light alternate</figcaption>
            </figure>
          </div>
        </article>

        <article className={styles.card}>
          <div className={styles.cardHead}>
            <h2>Maskable icon safe area</h2><span>512 × 512</span>
          </div>
          <div className={styles.maskStage}>
            <div className={styles.safeCircle}>
              <img src="/icons/cinewatch-maskable-icon-512.png" alt="Maskable icon" />
            </div>
          </div>
          <p className={styles.note}>Orange circle is a browser-only diagnostic overlay.</p>
        </article>

        <article className={`${styles.card} ${styles.wide}`}>
          <div className={styles.cardHead}>
            <h2>SEO / social exports</h2><span>Actual raster derivatives</span>
          </div>
          <div className={styles.socialGrid}>
            <figure>
              <div className={styles.mediaFrameWide}>
                <img src="/seo/cinewatch-og-1200x630.png" alt="Open Graph export" />
              </div>
              <figcaption>1200 × 630</figcaption>
            </figure>
            <figure>
              <div className={styles.mediaFrameSquare}>
                <img src="/seo/cinewatch-social-1080x1080.png" alt="Square social export" />
              </div>
              <figcaption>1080 × 1080</figcaption>
            </figure>
          </div>
        </article>
      </section>

      <section className={styles.checklist}>
        <h2>Human browser approval checklist</h2>
        <ul>
          <li>Complete lockups are visible — no clipped TV.</li>
          <li>Aperture-C color matches the approved A3 direction.</li>
          <li><strong>CineWatch</strong> remains one text color; only <strong>TV</strong> is aqua.</li>
          <li>R1A stays sharp at 64 px and above.</li>
          <li>M1 is legible at true 16 / 24 / 32 px.</li>
          <li>Chrome tab favicon is recognizable.</li>
          <li>App and maskable crops remain balanced.</li>
          <li>SEO/social exports show the complete brand lockup.</li>
          <li>No mobile horizontal overflow.</li>
        </ul>
      </section>
    </main>
  );
}
