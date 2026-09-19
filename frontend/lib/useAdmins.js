"use client";

import { useCallback, useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";

export function useAdmins() {
  const [admins, setAdmins] = useState([]);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      const data = await apiFetch("/api/admins");
      setAdmins(data.admins ?? data ?? []);
    } catch (err) {
      console.error("Failed to load admins:", err.message);
      setAdmins([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  // Admin-only. role is forced to "admin" server-side regardless of
  // anything sent — matches the same rule as employee signup.
  const createAdmin = useCallback(
    async ({ name, email, password }) => {
      const data = await apiFetch("/api/admins", {
        method: "POST",
        body: JSON.stringify({ name, email, password }),
      });
      await refresh();
      return data.admin ?? data;
    },
    [refresh]
  );

  // Admin-only. NOT part of the documented API contract — this hits the
  // standard REST convention (DELETE /api/admins/:id) as a best guess.
  // Confirm this route actually exists before relying on it.
  const deleteAdmin = useCallback(
    async (adminId) => {
      await apiFetch(`/api/admins/${adminId}`, {
        method: "DELETE",
      });
      await refresh();
    },
    [refresh]
  );

  return { admins, loading, refresh, createAdmin, deleteAdmin };
}