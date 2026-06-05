"use client";

import { usePathname } from "next/navigation";
import HomepageSupportClient from "./homepage-support-client";

export default function ClientFacingSupportWidget() {
  const pathname = usePathname() || "";

  const blocked =
    pathname === "/admin" ||
    pathname === "/admin-login" ||
    pathname.startsWith("/admin/") ||
    pathname.startsWith("/api/");

  if (blocked) return null;

  return <HomepageSupportClient />;
}
