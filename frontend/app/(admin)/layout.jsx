"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";

export default function AdminLayout({ children }) {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (loading) return;
    if (!user) {
      router.replace("/login");
    } else if (user.role !== "admin") {
      router.replace("/portal");
    }
  }, [user, loading, router]);

  if (loading || !user || user.role !== "admin") return null;

  return children;
}
