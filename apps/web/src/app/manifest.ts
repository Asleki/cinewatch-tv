import type { MetadataRoute } from "next";

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "CineWatch TV",
    short_name: "CineWatch TV",
    description: "CineWatch TV V1 private development application.",
    start_url: "/",
    display: "standalone",
    background_color: "#071A2D",
    theme_color: "#071A2D",
    icons: [
      {
        src: "/icons/cinewatch-app-icon-192.png",
        sizes: "192x192",
        type: "image/png",
        purpose: "any",
      },
      {
        src: "/icons/cinewatch-app-icon-512.png",
        sizes: "512x512",
        type: "image/png",
        purpose: "any",
      },
      {
        src: "/icons/cinewatch-maskable-icon-512.png",
        sizes: "512x512",
        type: "image/png",
        purpose: "maskable",
      },
    ],
  };
}
