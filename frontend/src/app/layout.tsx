import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import ClientFacingSupportWidget from "./client-facing-support-widget";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata = {
  title: "Ecommerce AI Agent Platform",
  description:
    "Premium white-label ecommerce AI agent platform for governed execution, product intelligence, UGC planning, influencer outreach, analytics optimisation, and secure deployment.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${geistSans.variable} ${geistMono.variable}`}>
      <body>{children}
        <ClientFacingSupportWidget /></body>
    </html>
  );
}
