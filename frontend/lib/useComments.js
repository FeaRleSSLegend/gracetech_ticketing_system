"use client";

import { useCallback, useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";

export function useComments(ticketId) {
  const [comments, setComments] = useState([]);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    if (!ticketId) return;
    setLoading(true);
    try {
      const data = await apiFetch(`/api/comments/${ticketId}`);
      setComments(data.comments ?? data ?? []);
    } catch (err) {
      console.error("Failed to load comments:", err.message);
      setComments([]);
    } finally {
      setLoading(false);
    }
  }, [ticketId]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  // author/userId is derived server-side from the auth token — not sent.
  const addComment = useCallback(
    async (body) => {
      const data = await apiFetch(`/api/comments/${ticketId}`, {
        method: "POST",
        body: JSON.stringify({ body }),
      });
      await refresh();
      return data.comment ?? data;
    },
    [ticketId, refresh]
  );

  return { comments, loading, refresh, addComment };
}