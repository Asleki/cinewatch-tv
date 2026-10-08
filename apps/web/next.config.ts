import type { NextConfig } from "next";

const cinewatchApiBase = (
  process.env.NEXT_PUBLIC_CINEWATCH_API_BASE_URL ?? "http://127.0.0.1:8000"
).replace(/\/+$/, "");

const nextConfig: NextConfig = {
  poweredByHeader: false,
  reactStrictMode: true,
  allowedDevOrigins: ["127.0.0.1"],
  async redirects() {
    return [{ source: "/under-development/stream-now", destination: "/stream-now", permanent: true }];
  },
  async rewrites() {
    return [
      {
        source: "/api/cinewatch/:path*",
        destination: `${cinewatchApiBase}/api/v1/:path*`,
      },
    ];
  },
};

export default nextConfig;
