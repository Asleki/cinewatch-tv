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
};

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
