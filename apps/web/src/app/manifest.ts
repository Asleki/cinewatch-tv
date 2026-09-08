import type { MetadataRoute } from "next";

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "CineWatch TV",
    short_name: "CineWatch TV",
    description: "CineWatch TV V1 private development application.",
    start_url: "/",
    display: "standalone",
  };
}
