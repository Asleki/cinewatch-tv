/** Presentation metadata for independently reviewed ORIGINAL provider assets.
 * Key by artwork, not organization name/ID or the viewer's theme. Original image
 * bytes are never transformed. Unclassified artwork receives a neutral light
 * matte; add an explicit reviewed entry when a new light mark needs dark support.
 */
export type LogoMatte = "light" | "dark";

const darkMatteAssets = new Set([
  "ybTppkzqb3XOWKNcco144BFlosB.png", // RTL II: white lettering
  "8PeKdSO13vYTod2HAJsV2m7mRr0.png", // Skydance Television: light orange
  "g5oRCNCi8kNVb8gEoSoIcqkhjmR.png", // Amazon MGM Studios: gold
  "ePTA7uHqE4k0exCefnacgljxjD.png", // Electric Hot Dog: bright multicolour
  "ygMQtjsKX7BZkCQhQZY82lgnCUO.png", // Atomic Monster: light figure/yellow
]);

export function getLogoMatte(src: string | null): LogoMatte {
  if (!src) return "light";
  try {
    const url = new URL(src);
    if (url.protocol !== "https:" || url.hostname !== "image.tmdb.org") return "light";
    const filename = url.pathname.split("/").at(-1) ?? "";
    return darkMatteAssets.has(filename) ? "dark" : "light";
  } catch {
    return "light";
  }
}
