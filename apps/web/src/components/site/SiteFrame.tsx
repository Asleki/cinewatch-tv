"use client";
/* eslint-disable @next/next/no-img-element */

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import type { ReactNode } from "react";
import { useEffect, useMemo, useRef, useState } from "react";

import styles from "./SiteFrame.module.css";

type SearchEntityType = "MOVIE" | "TV_SHOW" | "PERSON" | "GENRE" | "NETWORK_PROVIDER";

type SearchSuggestion = {
  entity_type: SearchEntityType;
  canonical_id: string;
  provider_id: number | null;
  label: string;
  secondary_text: string | null;
  image_url: string | null;
  destination: string;
  source: "tmdb" | "cinewatch";
};

type SearchResponse = {
  query: string;
  suggestions: SearchSuggestion[];
};

type IconName = "search" | "mic" | "sun" | "moon" | "user" | "home" | "play" | "compass" | "genres" | "cinema" | "close";

const primaryNavigation = [
  { label: "Home", href: "/" },
  { label: "Stream Now", href: "/under-development/stream-now" },
  { label: "Discover", href: "/discover/trending" },
  { label: "Genres", href: "/genres" },
  { label: "Cinema Guide", href: "/cinema-guide" },
] as const;

const footerGroups = [
  {
    title: "Watch",
    items: [
      ["Stream Now", "/under-development/stream-now"],
      ["Movies", "/discover/popular-movies?media_type=movie"],
      ["TV Shows", "/discover/popular-tv?media_type=tv"],
      ["Trailers", "/trailers"],
      ["Where to Watch", "/where-to-watch"],
    ],
  },
  {
    title: "Discover",
    items: [
      ["Genres", "/genres"],
      ["Networks", "/under-development/networks"],
      ["Countries & Cultures", "/under-development/countries-cultures"],
      ["People", "/under-development/people-index"],
      ["News", "/news"],
    ],
  },
  {
    title: "CineWatch Archives",
    items: [
      ["Film & Television", "/under-development/archive-film-tv"],
      ["Scripts", "/scripts"],
      ["Lyrics & Songs", "/lyrics"],
      ["NASA & Space", "/under-development/archive-space"],
      ["Historical Collections", "/under-development/archive-history"],
      ["Browse Archive", "/under-development/archive"],
    ],
  },
  {
    title: "CineWatch",
    items: [
      ["About", "/under-development/about"],
      ["Creators", "/under-development/creators"],
      ["Careers", "/under-development/careers"],
      ["Contact", "/contact"],
    ],
  },
  {
    title: "Support",
    items: [
      ["Help Center", "/under-development/help"],
      ["Accessibility", "/under-development/accessibility"],
      ["Privacy Policy", "/under-development/privacy"],
      ["Terms of Service", "/under-development/terms"],
      ["Rights & Copyright", "/under-development/rights"],
    ],
  },
] as const;

function Icon({ name }: { name: IconName }) {
  const common = { width: 20, height: 20, viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: 1.8, strokeLinecap: "round" as const, strokeLinejoin: "round" as const, "aria-hidden": true };
  if (name === "search") return <svg {...common}><circle cx="11" cy="11" r="6.5" /><path d="m16 16 4 4" /></svg>;
  if (name === "mic") return <svg {...common}><rect x="9" y="3" width="6" height="11" rx="3" /><path d="M6.5 11.5a5.5 5.5 0 0 0 11 0M12 17v4M9 21h6" /></svg>;
  if (name === "sun") return <svg {...common}><circle cx="12" cy="12" r="4" /><path d="M12 2v2M12 20v2M4.93 4.93l1.42 1.42M17.65 17.65l1.42 1.42M2 12h2M20 12h2M4.93 19.07l1.42-1.42M17.65 6.35l1.42-1.42" /></svg>;
  if (name === "moon") return <svg {...common}><path d="M20.5 15.5A8.5 8.5 0 0 1 8.5 3.5 8.5 8.5 0 1 0 20.5 15.5Z" /></svg>;
  if (name === "user") return <svg {...common}><circle cx="12" cy="8" r="3.5" /><path d="M5 21a7 7 0 0 1 14 0" /></svg>;
  if (name === "home") return <svg {...common}><path d="m3 11 9-8 9 8" /><path d="M5 10v10h14V10M9 20v-6h6v6" /></svg>;
  if (name === "play") return <svg {...common}><rect x="3" y="5" width="18" height="14" rx="3" /><path d="m10 9 5 3-5 3Z" /></svg>;
  if (name === "compass") return <svg {...common}><circle cx="12" cy="12" r="9" /><path d="m15.5 8.5-2.2 4.8-4.8 2.2 2.2-4.8Z" /></svg>;
  if (name === "genres") return <svg {...common}><path d="M4 5h6v6H4zM14 5h6v6h-6zM4 15h6v5H4zM14 15h6v5h-6z" /></svg>;
  if (name === "cinema") return <svg {...common}><rect x="3" y="6" width="18" height="13" rx="2" /><path d="M7 6V3m5 3V3m5 3V3M3 10h18" /></svg>;
  return <svg {...common}><path d="m6 6 12 12M18 6 6 18" /></svg>;
}

function entityLabel(type: SearchEntityType): string {
  if (type === "TV_SHOW") return "TV";
  if (type === "NETWORK_PROVIDER") return "Provider";
  return type.charAt(0) + type.slice(1).toLocaleLowerCase();
}

function isRouteActive(pathname: string | null, href: string): boolean {
  if (!pathname) return false;
  if (href === "/") return pathname === "/";
  if (href.startsWith("/under-development/stream-now")) return pathname.includes("stream-now");
  return pathname.startsWith(href.split("?")[0]);
}

export default function SiteFrame({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  if (pathname?.startsWith("/brand-qualification")) return <>{children}</>;
  return <ProductSiteFrame>{children}</ProductSiteFrame>;
}

function ProductSiteFrame({ children }: { children: ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const searchWrap = useRef<HTMLDivElement | null>(null);
  const [query, setQuery] = useState("");
  const [suggestions, setSuggestions] = useState<SearchSuggestion[]>([]);
  const [searchOpen, setSearchOpen] = useState(false);
  const [searchState, setSearchState] = useState<"idle" | "loading" | "ready" | "empty" | "error">("idle");
  const [theme, setTheme] = useState<"dark" | "light">("dark");
  const [initialReady, setInitialReady] = useState(false);

  useEffect(() => {
    const stored = window.localStorage.getItem("cinewatch-theme");
    const preferred = window.matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark";
    const resolved = stored === "light" || stored === "dark" ? stored : preferred;
    document.documentElement.dataset.theme = resolved;
    const themeTimer = window.setTimeout(() => setTheme(resolved), 0);

    const startupKey = "cinewatch-startup-ready-v1";
    if (window.sessionStorage.getItem(startupKey) === "1") {
      const readyTimer = window.setTimeout(() => setInitialReady(true), 0);
      return () => {
        window.clearTimeout(themeTimer);
        window.clearTimeout(readyTimer);
      };
    }
    const readyTimer = window.setTimeout(() => {
      window.sessionStorage.setItem(startupKey, "1");
      setInitialReady(true);
    }, 3000);
    return () => {
      window.clearTimeout(themeTimer);
      window.clearTimeout(readyTimer);
    };
  }, []);

  useEffect(() => {
    const normalized = query.trim();
    if (normalized.length < 2) {
      const resetTimer = window.setTimeout(() => {
        setSuggestions([]);
        setSearchState("idle");
      }, 0);
      return () => window.clearTimeout(resetTimer);
    }
    const controller = new AbortController();
    const timer = window.setTimeout(async () => {
      setSearchState("loading");
      try {
        const response = await fetch(`/api/cinewatch/search?q=${encodeURIComponent(normalized)}`, {
          cache: "no-store",
          signal: controller.signal,
          headers: { Accept: "application/json" },
        });
        if (!response.ok) throw new Error(`search ${response.status}`);
        const payload = await response.json() as SearchResponse;
        const next = (payload.suggestions ?? []).slice(0, 5);
        setSuggestions(next);
        setSearchState(next.length ? "ready" : "empty");
      } catch {
        if (controller.signal.aborted) return;
        setSuggestions([]);
        setSearchState("error");
      }
    }, 320);
    return () => {
      controller.abort();
      window.clearTimeout(timer);
    };
  }, [query]);

  useEffect(() => {
    function closeOnOutsidePointer(event: PointerEvent) {
      if (searchWrap.current && !searchWrap.current.contains(event.target as Node)) setSearchOpen(false);
    }
    document.addEventListener("pointerdown", closeOnOutsidePointer);
    return () => document.removeEventListener("pointerdown", closeOnOutsidePointer);
  }, []);

  const logo = theme === "light" ? "/brand/cinewatch-lockup-on-light.svg" : "/brand/cinewatch-lockup-on-dark.svg";
  const mobileItems = useMemo(() => [
    { ...primaryNavigation[0], icon: "home" as IconName },
    { ...primaryNavigation[1], icon: "play" as IconName },
    { ...primaryNavigation[2], icon: "compass" as IconName },
    { ...primaryNavigation[3], icon: "genres" as IconName },
    { ...primaryNavigation[4], icon: "cinema" as IconName },
  ], []);

  function toggleTheme() {
    const next = theme === "light" ? "dark" : "light";
    setTheme(next);
    document.documentElement.dataset.theme = next;
    window.localStorage.setItem("cinewatch-theme", next);
  }

  function chooseSuggestion(item: SearchSuggestion) {
    setQuery(item.label);
    setSearchOpen(false);
    router.push(item.destination);
  }

  return (
    <div className={styles.shell}>
      {!initialReady ? (
        <div className={styles.readiness} role="status" aria-live="polite">
          <img src="/brand/cinewatch-mark-r1a-full.svg" alt="" />
          <strong>Getting CineWatch ready for you...</strong>
          <span>Connecting the stories, people and discovery services you asked for.</span>
        </div>
      ) : null}

      <header className={styles.header}>
        <Link className={styles.brand} href="/" aria-label="CineWatch TV home">
          <img src={logo} alt="CineWatch TV" />
        </Link>

        <nav className={styles.desktopNav} aria-label="Primary navigation">
          {primaryNavigation.map((item) => (
            <Link key={item.label} href={item.href} className={isRouteActive(pathname, item.href) ? styles.activeNav : undefined}>
              {item.label}
            </Link>
          ))}
        </nav>

        <div className={styles.searchWrap} ref={searchWrap}>
          <label className={styles.searchBox}>
            <Icon name="search" />
            <input
              value={query}
              onChange={(event) => {
                setQuery(event.target.value);
                setSearchOpen(true);
              }}
              onFocus={() => setSearchOpen(true)}
              placeholder="Search movies, TV, people, genres, providers..."
              aria-label="Search CineWatch"
              autoComplete="off"
            />
            {query ? (
              <button type="button" onClick={() => { setQuery(""); setSuggestions([]); setSearchState("idle"); }} aria-label="Clear search">
                <Icon name="close" />
              </button>
            ) : null}
            <button type="button" onClick={() => router.push("/voice-lab")} aria-label="Open NexVox Voice Lab" title="NexVox Voice Lab">
              <Icon name="mic" />
            </button>
          </label>

          {searchOpen && query.trim().length >= 2 ? (
            <div className={styles.suggestions} role="listbox" aria-label="Search suggestions">
              {searchState === "loading" ? <p className={styles.inlineLoading}><span aria-hidden="true" />Searching…</p> : null}
              {searchState === "error" ? <p>Search is temporarily unavailable.</p> : null}
              {searchState === "empty" ? <p>No CineWatch entities matched this search.</p> : null}
              {suggestions.map((item) => (
                <button key={item.canonical_id} type="button" role="option" aria-selected="false" onClick={() => chooseSuggestion(item)}>
                  {item.image_url ? <img src={item.image_url} alt="" /> : <span className={styles.suggestionGlyph}>{entityLabel(item.entity_type).slice(0, 1)}</span>}
                  <span className={styles.suggestionCopy}>
                    <strong>{item.label}</strong>
                    <small>{item.secondary_text ?? entityLabel(item.entity_type)}</small>
                  </span>
                  <b className={styles.entityBadge}>{entityLabel(item.entity_type)}</b>
                </button>
              ))}
            </div>
          ) : null}
        </div>

        <button type="button" className={styles.modeButton} onClick={toggleTheme} aria-label="Toggle color mode">
          <Icon name={theme === "light" ? "moon" : "sun"} />
        </button>
        <Link className={styles.accountButton} href="/under-development/account" aria-label="Account">
          <Icon name="user" />
        </Link>
      </header>

      <main className={styles.main}>{children}</main>

      <footer className={styles.footer}>
        <div className={styles.footerBrand}>
          <img src={logo} alt="CineWatch TV" />
          <p>Cinema brings you closer to the stories that move the world. Stream. Discover. Belong.</p>
          <small>© 2026 CineWatch TV. All rights reserved.</small>
        </div>
        {footerGroups.map((group) => <FooterGroup key={group.title} title={group.title} items={group.items} />)}
        <div className={styles.footerMeta}>Explore stories, people, trailers, news and entertainment references across CineWatch TV. Built by NexTech.</div>
      </footer>

      <nav className={styles.mobileNav} aria-label="Mobile navigation">
        {mobileItems.map((item) => (
          <Link key={item.label} href={item.href} className={isRouteActive(pathname, item.href) ? styles.mobileActive : undefined}>
            <Icon name={item.icon} />
            {item.label === "Cinema Guide" ? "Cinema" : item.label}
          </Link>
        ))}
      </nav>
    </div>
  );
}

function FooterGroup({ title, items }: { title: string; items: readonly (readonly [string, string])[] }) {
  return (
    <section className={styles.footerGroup} aria-label={title}>
      <h2>{title}</h2>
      {items.map(([label, href]) => <Link key={label} href={href}>{label}</Link>)}
    </section>
  );
}
