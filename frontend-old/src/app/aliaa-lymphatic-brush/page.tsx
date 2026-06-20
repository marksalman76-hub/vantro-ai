import type { Metadata } from "next";
import AliaaProductPage from "./AliaaProductPage";

export const metadata: Metadata = {
  title: "Lymphatic Brush - Sculpt Your Face in 3 Minutes | aliaa",
  description:
    "Premium lymphatic drainage brush for instant puffiness reduction and jaw sculpting. 4.9 stars from 3,200+ customers. 30-day guarantee.",
  openGraph: {
    title: "aliaa Lymphatic Brush",
    description:
      "Lymphatic drainage and facial contouring in one ergonomic brush.",
    type: "website",
  },
};

export default function Page() {
  return <AliaaProductPage />;
}
