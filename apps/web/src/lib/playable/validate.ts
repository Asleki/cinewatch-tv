import type { PlayableManifest } from "./types";

/** Shape validation only. Playback permission is decided on the server. */
export function assertPlayableManifest(value: unknown): PlayableManifest {
  if (!value || typeof value !== "object") throw new Error("Invalid playable manifest");
  const manifest = value as PlayableManifest;
  const text = (v: unknown): v is string => typeof v === "string" && v.trim().length > 0;
  const mediaUrl = (v: unknown): boolean => {
    if (!text(v)) return false;
    // Same-origin protected delivery or a future signed HTTPS source. Never arbitrary schemes.
    if (v.startsWith("/") && !v.startsWith("//") && !v.includes("\\")) return true;
    try { const url = new URL(v); return url.protocol === "https:" && !url.username && !url.password; }
    catch { return false; }
  };
  if (!text(manifest.playableId) || !text(manifest.title)) throw new Error("Playable identity and title required");
  if (manifest.kind !== "movie" && manifest.kind !== "episode") throw new Error("Invalid playable kind");
  if (manifest.episodeLabel !== undefined && !text(manifest.episodeLabel)) throw new Error("Invalid episode label");
  if (!Array.isArray(manifest.sources) || !manifest.sources.length) throw new Error("Playback source required");
  const ids = new Set<string>();
  for (const source of manifest.sources) {
    if (!source || !text(source.id) || ids.has(source.id) || !mediaUrl(source.src) ||
        !text(source.label) || !["video/mp4", "video/webm"].includes(source.mimeType)) throw new Error("Invalid playback source");
    ids.add(source.id);
  }
  if (!Array.isArray(manifest.subtitles)) throw new Error("Subtitle array required");
  const trackIds = new Set<string>();
  let defaults = 0;
  for (const track of manifest.subtitles) {
    if (!track || !text(track.id) || trackIds.has(track.id) || !text(track.language) || !text(track.label) ||
        !mediaUrl(track.src) || track.format !== "vtt" || (track.default !== undefined && typeof track.default !== "boolean")) throw new Error("Invalid subtitle track");
    trackIds.add(track.id);
    if (track.default) defaults++;
  }
  if (defaults > 1) throw new Error("Multiple default subtitle tracks");
  if (!manifest.capabilities || [manifest.capabilities.pictureInPicture, manifest.capabilities.playbackSpeed,
    manifest.capabilities.subtitles].some(v => typeof v !== "boolean")) throw new Error("Invalid player capabilities");
  return manifest;
}
