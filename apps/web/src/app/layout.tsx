import type { Metadata } from "next";
import type { ReactNode } from "react";

import { getPublicSiteUrl } from "@/lib/config/public-env";

import "./globals.css";

export const metadata: Metadata = {
  metadataBase: getPublicSiteUrl(),
  applicationName: "CineWatch TV",
  title: {
    default: "CineWatch TV",
    template: "%s | CineWatch TV",
  },
  description: "CineWatch TV V1 private development application.",
  robots: {
    index: false,
    follow: false,
  },
  icons: {
    icon: [
      { url: "/icons/cinewatch-favicon-16.png", sizes: "16x16", type: "image/png" },
      { url: "/icons/cinewatch-favicon-32.png", sizes: "32x32", type: "image/png" },
      { url: "/icons/cinewatch-favicon-48.png", sizes: "48x48", type: "image/png" },
    ],
    apple: [
      { url: "/icons/cinewatch-app-icon-180.png", sizes: "180x180", type: "image/png" },
    ],
  },
  openGraph: {
    title: "CineWatch TV",
    siteName: "CineWatch TV",
    type: "website",
    images: [
      {
        url: "/seo/cinewatch-og-1200x630.png",
        width: 1200,
        height: 630,
        alt: "CineWatch TV",
      },
    ],
  },
};

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
