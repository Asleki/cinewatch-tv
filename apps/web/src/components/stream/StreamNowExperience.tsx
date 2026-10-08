import { CineWatchPlayer } from "@/components/player/CineWatchPlayer";
import type { PlayableManifest } from "@/lib/playable/types";
import StreamNowAnimation from "./StreamNowAnimation";

/** Server composition: callers must resolve permission before passing a manifest. */
export default function StreamNowExperience({ manifest }: { manifest: PlayableManifest | null }) {
  return manifest ? <CineWatchPlayer manifest={manifest} /> : <StreamNowAnimation />;
}
