"use client";
/* eslint-disable @next/next/no-img-element */

import type { HomeGenreEntry, HomeSearchSuggestion } from "@cinewatch/contracts";
import { usePathname, useRouter } from "next/navigation";
import type { ReactNode } from "react";
import { useEffect, useMemo, useRef, useState } from "react";

import styles from "./SiteFrame.module.css";

type LocalSuggestion = {
  label: string;
  kind: "genre" | "country" | "collection";
  futurePath: string;
  secondaryText: string;
};

type DisplaySuggestion = {
  key: string;
  label: string;
  secondaryText: string | null;
  imageUrl: string | null;
  futurePath: string;
  kind: string;
};

type SpeechRecognitionResultEventLike = Event & {
  results: ArrayLike<{ 0: { transcript: string } }>;
};

type SpeechRecognitionLike = {
  lang: string;
  interimResults: boolean;
  maxAlternatives: number;
  onresult: ((event: SpeechRecognitionResultEventLike) => void) | null;
  onerror: (() => void) | null;
  onend: (() => void) | null;
  start: () => void;
};

type SpeechRecognitionConstructor = new () => SpeechRecognitionLike;

type IconName = "search" | "mic" | "sun" | "moon" | "user" | "home" | "play" | "compass" | "list" | "more" | "close";

const editorialDiscovery: LocalSuggestion[] = [
  { label: "Kenyan Stories", kind: "collection", futurePath: "/discover/kenyan-stories", secondaryText: "CineWatch discovery" },
  { label: "Bollywood", kind: "collection", futurePath: "/discover/bollywood", secondaryText: "CineWatch discovery" },
  { label: "Nollywood", kind: "collection", futurePath: "/discover/nollywood", secondaryText: "CineWatch discovery" },
  { label: "K-Drama", kind: "collection", futurePath: "/discover/k-drama", secondaryText: "CineWatch discovery" },
  { label: "Chinese", kind: "collection", futurePath: "/discover/chinese", secondaryText: "CineWatch discovery" },
  { label: "Hollywood", kind: "collection", futurePath: "/discover/hollywood", secondaryText: "CineWatch discovery" },
  { label: "Tyler Perry", kind: "collection", futurePath: "/discover/tyler-perry", secondaryText: "CineWatch discovery" },
  { label: "Kenya", kind: "country", futurePath: "/country/KE", secondaryText: "Country & culture" },
  { label: "Nigeria", kind: "country", futurePath: "/country/NG", secondaryText: "Country & culture" },
  { label: "India", kind: "country", futurePath: "/country/IN", secondaryText: "Country & culture" },
  { label: "South Korea", kind: "country", futurePath: "/country/KR", secondaryText: "Country & culture" },
  { label: "China", kind: "country", futurePath: "/country/CN", secondaryText: "Country & culture" },
  { label: "United States", kind: "country", futurePath: "/country/US", secondaryText: "Country & culture" },
  { label: "United Kingdom", kind: "country", futurePath: "/country/GB", secondaryText: "Country & culture" },
  { label: "South Africa", kind: "country", futurePath: "/country/ZA", secondaryText: "Country & culture" },
  { label: "Ghana", kind: "country", futurePath: "/country/GH", secondaryText: "Country & culture" },
];

function Icon({ name }: { name: IconName }) {
  const common = { width: 18, height: 18, viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: 1.8, strokeLinecap: "round" as const, strokeLinejoin: "round" as const, "aria-hidden": true };
  if (name === "search") return <svg {...common}><circle cx="11" cy="11" r="6.5" /><path d="m16 16 4 4" /></svg>;
  if (name === "mic") return <svg {...common}><rect x="9" y="3" width="6" height="11" rx="3" /><path d="M6.5 11.5a5.5 5.5 0 0 0 11 0M12 17v4M9 21h6" /></svg>;
  if (name === "sun") return <svg {...common}><circle cx="12" cy="12" r="4" /><path d="M12 2v2M12 20v2M4.93 4.93l1.42 1.42M17.65 17.65l1.42 1.42M2 12h2M20 12h2M4.93 19.07l1.42-1.42M17.65 6.35l1.42-1.42" /></svg>;
  if (name === "moon") return <svg {...common}><path d="M20.5 15.5A8.5 8.5 0 0 1 8.5 3.5 8.5 8.5 0 1 0 20.5 15.5Z" /></svg>;
  if (name === "user") return <svg {...common}><circle cx="12" cy="8" r="3.5" /><path d="M5 21a7 7 0 0 1 14 0" /></svg>;
  if (name === "home") return <svg {...common}><path d="m3 11 9-8 9 8" /><path d="M5 10v10h14V10M9 20v-6h6v6" /></svg>;
  if (name === "play") return <svg {...common}><rect x="3" y="5" width="18" height="14" rx="3" /><path d="m10 9 5 3-5 3Z" /></svg>;
  if (name === "compass") return <svg {...common}><circle cx="12" cy="12" r="9" /><path d="m15.5 8.5-2.2 4.8-4.8 2.2 2.2-4.8Z" /></svg>;
  if (name === "list") return <svg {...common}><path d="M6 6h15M6 12h15M6 18h15" /><circle cx="3" cy="6" r=".7" fill="currentColor" stroke="none" /><circle cx="3" cy="12" r=".7" fill="currentColor" stroke="none" /><circle cx="3" cy="18" r=".7" fill="currentColor" stroke="none" /></svg>;
  if (name === "close") return <svg {...common}><path d="m6 6 12 12M18 6 6 18" /></svg>;
  return <svg {...common}><circle cx="5" cy="12" r="1" fill="currentColor" stroke="none" /><circle cx="12" cy="12" r="1" fill="currentColor" stroke="none" /><circle cx="19" cy="12" r="1" fill="currentColor" stroke="none" /></svg>;
}

function normalizeApiSuggestion(item: HomeSearchSuggestion): DisplaySuggestion {
  return {
    key: `${item.media_type}-${item.provider_id}`,
    label: item.label,
    secondaryText: item.secondary_text ?? item.media_type,
    imageUrl: item.image_url ?? null,
    futurePath: item.future_path,
    kind: item.media_type,
  };
}

function searchLocal(query: string, genres: HomeGenreEntry[]): DisplaySuggestion[] {
  const needle = query.toLocaleLowerCase();
  const genreMatches = genres
    .filter((genre) => genre.name.toLocaleLowerCase().includes(needle))
    .slice(0, 3)
    .map((genre) => ({
      key: `genre-${genre.slug}`,
      label: genre.name,
      secondaryText: "Genre",
      imageUrl: null,
      futurePath: genre.future_path,
      kind: "genre",
    }));
  const editorialMatches = editorialDiscovery
    .filter((item) => item.label.toLocaleLowerCase().includes(needle))
    .slice(0, 3)
    .map((item) => ({
      key: `${item.kind}-${item.futurePath}`,
      label: item.label,
      secondaryText: item.secondaryText,
      imageUrl: null,
      futurePath: item.futurePath,
      kind: item.kind,
    }));
  return [...genreMatches, ...editorialMatches];
}

export default function SiteFrame({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  if (pathname?.startsWith("/brand-qualification")) return <>{children}</>;
  return <ProductSiteFrame>{children}</ProductSiteFrame>;
}

function ProductSiteFrame({ children }: { children: ReactNode }) {
    const router = useRouter();
  const pathname = usePathname();
const [query, setQuery] = useState("");
  const [apiSuggestions, setApiSuggestions] = useState<HomeSearchSuggestion[]>([]);
  const [genres, setGenres] = useState<HomeGenreEntry[]>([]);
  const [searchOpen, setSearchOpen] = useState(false);
  const [listening, setListening] = useState(false);
  const [theme, setTheme] = useState<"dark" | "light">("dark");
  const searchSequence = useRef(0);
  const searchWrap = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const frame = window.requestAnimationFrame(() => {
      const stored = window.localStorage.getItem("cinewatch-theme");
      const preferred = window.matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark";
      const resolved = stored === "light" || stored === "dark" ? stored : preferred;
      document.documentElement.dataset.theme = resolved;
      setTheme(resolved);
    });
    return () => window.cancelAnimationFrame(frame);
  }, []);

  useEffect(() => {
    fetch("/api/cinewatch/home/genres", { cache: "no-store" })
      .then((response) => (response.ok ? response.json() : null))
      .then((payload) => setGenres(payload?.genres ?? []))
      .catch(() => setGenres([]));
  }, []);

  useEffect(() => {
    const normalized = query.trim();
    if (normalized.length < 2) return;
    const sequence = ++searchSequence.current;
    const timeout = window.setTimeout(() => {
      fetch(`/api/cinewatch/home/search?q=${encodeURIComponent(normalized)}`, { cache: "no-store" })
        .then((response) => (response.ok ? response.json() : null))
        .then((payload) => {
          if (sequence === searchSequence.current) setApiSuggestions(payload?.suggestions ?? []);
        })
        .catch(() => {
          if (sequence === searchSequence.current) setApiSuggestions([]);
        });
    }, 320);
    return () => window.clearTimeout(timeout);
  }, [query]);

  useEffect(() => {
    function closeOnOutsidePointer(event: PointerEvent) {
      if (searchWrap.current && !searchWrap.current.contains(event.target as Node)) setSearchOpen(false);
    }
    document.addEventListener("pointerdown", closeOnOutsidePointer);
    return () => document.removeEventListener("pointerdown", closeOnOutsidePointer);
  }, []);

  const suggestions = useMemo(() => {
    if (query.trim().length < 2) return [];
    const combined = [...apiSuggestions.map(normalizeApiSuggestion), ...searchLocal(query.trim(), genres)];
    const seen = new Set<string>();
    return combined.filter((item) => {
      if (seen.has(item.futurePath)) return false;
      seen.add(item.futurePath);
      return true;
    }).slice(0, 8);
  }, [apiSuggestions, genres, query]);

  const logo = theme === "light" ? "/brand/cinewatch-lockup-on-light.svg" : "/brand/cinewatch-lockup-on-dark.svg";

  function toggleTheme() {
    const next = theme === "light" ? "dark" : "light";
    setTheme(next);
    document.documentElement.dataset.theme = next;
    window.localStorage.setItem("cinewatch-theme", next);
  }

  function startVoiceSearch() {
    const windowWithSpeech = window as typeof window & {
      SpeechRecognition?: SpeechRecognitionConstructor;
      webkitSpeechRecognition?: SpeechRecognitionConstructor;
    };
    const Constructor = windowWithSpeech.SpeechRecognition ?? windowWithSpeech.webkitSpeechRecognition;
    if (!Constructor) return;
    const recognition = new Constructor();
    recognition.lang = "en-US";
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;
    recognition.onresult = (event) => {
      const transcript = event.results[0]?.[0]?.transcript?.trim();
      if (transcript) {
        setQuery(transcript);
        setSearchOpen(true);
      }
    };
    recognition.onerror = () => setListening(false);
    recognition.onend = () => setListening(false);
    setListening(true);
    recognition.start();
  }

  return (
    <div className={styles.shell}>
      <header className={styles.header}>
        <a className={styles.brand} href="#top" aria-label="CineWatch TV home">
          <img src={logo} alt="CineWatch TV" />
        </a>
        <nav className={styles.desktopNav} aria-label="Primary navigation">
        <a
          href="#top"
          className={pathname === "/" ? styles.activeNav : undefined}
        >
          Home
        </a>
        <a href="#stream-now">Stream Now</a>
        <a href="#discover">Discover</a>
        <a
          href="/genres"
          className={
            pathname?.startsWith("/genre")
              ? styles.activeNav
              : undefined
          }
        >
          Genres
        </a>
        <a
          href="/cinema-guide"
          className={
            pathname?.startsWith("/cinema-guide")
              ? styles.activeNav
              : undefined
          }
        >
          Cinema Guide
        </a>
      </nav>
        <div className={styles.searchWrap} ref={searchWrap}>
          <label className={styles.searchBox}>
            <Icon name="search" />
            <input
              value={query}
              onChange={(event) => {
                const nextQuery = event.target.value;
                setQuery(nextQuery);
                if (nextQuery.trim().length < 2) setApiSuggestions([]);
                setSearchOpen(true);
              }}
              onFocus={() => setSearchOpen(true)}
              placeholder="Search movies, shows, genres, people…"
              aria-label="Search CineWatch"
            />
            {query ? (
              <button
                type="button"
                onClick={() => {
                  setQuery("");
                  setApiSuggestions([]);
                }}
                aria-label="Clear search"
              >
                <Icon name="close" />
              </button>
            ) : null}
            <button
              type="button"
              onClick={startVoiceSearch}
              aria-label="Voice search"
              className={listening ? styles.listening : undefined}
              title={listening ? "Listening…" : "Voice search"}
            >
              <Icon name="mic" />
            </button>
          </label>
          {searchOpen && suggestions.length > 0 ? (
            <div className={styles.suggestions} role="listbox" aria-label="Search suggestions">
              {suggestions.map((item) => (
                <button
                  key={item.key}
                  type="button"
                  role="option"
                  aria-selected={query === item.label}
                  data-future-path={item.futurePath}
                  onClick={() => {
                    setQuery(item.label);
                    setSearchOpen(false);
                router.push(item.futurePath);
                  }}
                >
                  {item.imageUrl ? <img src={item.imageUrl} alt="" /> : <span className={styles.suggestionGlyph}>{item.kind.slice(0, 1).toUpperCase()}</span>}
                  <span>
                    <strong>{item.label}</strong>
                    <small>{item.secondaryText}</small>
                  </span>
                </button>
              ))}
              <p>Suggestions stay on Home for now; their future destinations are already preserved.</p>
            </div>
          ) : null}
        </div>
        <button type="button" className={styles.modeButton} onClick={toggleTheme} aria-label="Toggle color mode">
          <Icon name={theme === "light" ? "moon" : "sun"} />
        </button>
        <button type="button" className={styles.accountButton} aria-label="Account placeholder"><Icon name="user" /></button>
      </header>

      <main id="top" className={styles.main}>{children}</main>

      <footer className={styles.footer}>
        <div className={styles.footerBrand}>
          <img src={logo} alt="CineWatch TV" />
          <p>Cinema brings you closer to the stories that move the world. Stream. Discover. Belong.</p>
          <small>© 2026 CineWatch TV. All rights reserved.</small>
        </div>
        <FooterGroup title="Watch" items={["Stream Now", "Movies", "TV Shows", "Trailers"]} />
        <FooterGroup title="Discover" items={["Genres", "Networks", "Countries & Cultures", "People", "News"]} />
        <FooterGroup title="CineWatch Archives" items={["Film & Television", "Scripts", "NASA & Space", "Historical Collections", "Browse Archive"]} />
        <FooterGroup title="CineWatch" items={["About", "Creators", "Careers", "Contact"]} />
        <FooterGroup title="Support" items={["Help Center", "Accessibility", "Privacy Policy", "Terms of Service", "Rights & Copyright"]} />
        <div className={styles.footerMeta}>Powered by TMDb and governed CineWatch provider services. Built by NexTech.</div>
      </footer>

      <nav className={styles.mobileNav} aria-label="Mobile navigation">
        <a href="#top"><Icon name="home" />Home</a>
        <a href="#stream-now"><Icon name="play" />Stream Now</a>
        <a href="#discover"><Icon name="compass" />Discover</a>
        <button type="button" disabled><Icon name="list" />My List</button>
        <button type="button" disabled><Icon name="more" />More</button>
      </nav>
    </div>
  );
}

function FooterGroup({ title, items }: { title: string; items: string[] }) {
  return (
    <section className={styles.footerGroup} aria-label={title}>
      <h2>{title}</h2>
      {items.map((item) => <span key={item} aria-disabled="true">{item}</span>)}
    </section>
  );
}
