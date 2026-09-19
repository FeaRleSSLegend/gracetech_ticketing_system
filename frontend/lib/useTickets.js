"use client";

import { useCallback, useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";

export function useTickets() {
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      const data = await apiFetch("/api/tickets/");
      setTickets(data.tickets ?? data ?? []);
    } catch (err) {
      // Fetch failed (network hiccup, backend cold-starting, etc.) — fall
      // back to an empty list rather than leaving stale/undefined data, and
      // let the loading spinner clear either way so the UI can show its
      // proper empty state instead of spinning forever.
      console.error("Failed to load tickets:", err.message);
      setTickets([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  // createdBy is derived server-side from the auth token — not sent here.
  const createTicket = useCallback(
    async ({ category, comment, office }) => {
      const data = await apiFetch("/api/tickets/", {
        method: "POST",
        body: JSON.stringify({ category, comment, office }),
      });
      await refresh();
      return data.ticket ?? data;
    },
    [refresh]
  );

  // Admin-only. No request body — the claiming admin is read from the
  // token. Backend returns 409 if someone else already claimed it.
  const claimTicket = useCallback(
    async (ticketId) => {
      const data = await apiFetch(`/api/tickets/${ticketId}/claim`, {
        method: "POST",
      });
      await refresh();
      return data.ticket ?? data;
    },
    [refresh]
  );

  // Admin-only. status must be "resolved" or "closed" — the ticket must
  // already be in_progress (i.e. claimed) or the backend returns 409.
  const updateTicketStatus = useCallback(
    async (ticketId, status) => {
      const data = await apiFetch(`/api/tickets/${ticketId}`, {
        method: "PATCH",
        body: JSON.stringify({ status }),
      });
      await refresh();
      return data.ticket ?? data;
    },
    [refresh]
  );

  // Admin-only. NOT part of the documented API contract — this hits the
  // standard REST convention (DELETE /api/tickets/:id) as a best guess.
  // Confirm this route actually exists on the backend before relying on it.
  const deleteTicket = useCallback(
    async (ticketId) => {
      await apiFetch(`/api/tickets/${ticketId}`, {
        method: "DELETE",
      });
      await refresh();
    },
    [refresh]
  );

  return {
    tickets,
    loading,
    refresh,
    createTicket,
    claimTicket,
    updateTicketStatus,
    deleteTicket,
  };
}