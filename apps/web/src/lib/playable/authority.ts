import "server-only";
import type { PlayableManifest, PlayableKind } from "./types";

export type PlaybackIdentity = { kind: PlayableKind; id: string };

/**
 * The production authority is deliberately closed until rights, viewer access,
 * territory and protected delivery are implemented and qualified together.
 * A discovery-provider ID or browser-supplied manifest never grants access.
 * No lab fixture, public demo or environment URL is a production source.
 */
export async function resolveAuthorizedPlayback(
  identity: PlaybackIdentity | null,
): Promise<PlayableManifest | null> {
  // This zero-source authority has no configured permit, for any identity.
  // Replace this server-only decision in the authorized media-onboarding milestone.
  void identity;
  return null;
}
