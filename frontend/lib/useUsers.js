"use client";

import { useCallback, useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";

// NOT part of the documented API contract — built against the standard
// REST convention (GET/DELETE /api/users) as a best guess, mirroring how
// admin management works via /api/admins. Confirm this route exists before
// relying on it.
export function useUsers() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      const data = await apiFetch("/api/users");
      setUsers(data.users ?? data ?? []);
    } catch (err) {
      console.error("Failed to load users:", err.message);
      setUsers([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  // Admin-only.
  const deleteUser = useCallback(
    async (userId) => {
      await apiFetch(`/api/users/${userId}`, {
        method: "DELETE",
      });
      await refresh();
    },
    [refresh]
  );

  return { users, loading, refresh, deleteUser };
}