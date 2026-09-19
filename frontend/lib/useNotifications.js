"use client";

import { useCallback, useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";

// name should be the logged-in user's own name (works for employees and
// admins alike now — the endpoint isn't admin-only anymore). Employees will
// get broadcasts (new_ticket/claimed) mixed in with their own targeted
// resolved/closed notifications — filter client-side on
// `recipientName !== null` if you only want their personal ones.
export function useNotifications(name) {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    if (!name) return;
    setLoading(true);
    try {
      const data = await apiFetch(`/api/notifications/?name=${encodeURIComponent(name)}`);
      const newestFirst = [...(data.notifications ?? [])].sort((a, b) => {
        const aTime = new Date(a.time ?? a.created_at ?? a.createdAt).getTime();
        const bTime = new Date(b.time ?? b.created_at ?? b.createdAt).getTime();

        if (Number.isNaN(aTime)) return 1;
        if (Number.isNaN(bTime)) return -1;
        return bTime - aTime;
      });
      setNotifications(newestFirst);
    } catch (err) {
      console.error("Failed to load notifications:", err.message);
      setNotifications([]);
    } finally {
      setLoading(false);
    }
  }, [name]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { notifications, loading, refresh };
}