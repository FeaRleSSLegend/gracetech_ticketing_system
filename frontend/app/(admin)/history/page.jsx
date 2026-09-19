"use client";

import { useState } from "react";
import Sidebar from "@/components/Sidebar";
import TopBar from "@/components/TopBar";
import TicketRow from "@/components/TicketRow";
import TicketDetailModal from "@/components/TicketDetailModal";
import Spinner from "@/components/Spinner";
import { useTickets } from "@/lib/useTickets";
import { useNotifications } from "@/lib/useNotifications";
import { useAuth } from "@/lib/auth-context";

export default function HistoryPage() {
  const { user } = useAuth();
  const { tickets, loading } = useTickets();
  const { notifications } = useNotifications(user?.name);
  const [selectedTicketId, setSelectedTicketId] = useState(null);

  const selectedTicket = tickets.find((t) => t.id === selectedTicketId) ?? null;

  return (
    <div className="flex flex-col md:flex-row bg-[#F6F7F9] min-h-screen font-sans">
      <Sidebar />
      <main className="flex-1 px-4 py-5 md:px-10 md:py-8">
        {/* No primary action here — History is a read-only log */}
        <TopBar title="History" notificationCount={notifications.length} />

        <div className="bg-white rounded-2xl border border-gray-100 p-5">
          <div className="flex items-center justify-between mb-4 px-1">
            <h2 className="text-base font-bold text-gray-900">
              All Tickets
            </h2>
            <span className="text-xs text-gray-400">
              {tickets.length} total
            </span>
          </div>

          <div className="space-y-2">
            {loading ? (
              <div className="flex items-center justify-center gap-2 px-1 py-6 text-center text-gray-400 text-sm">
                <Spinner size={16} />
                Loading tickets…
              </div>
            ) : tickets.length > 0 ? (
              tickets.map((t) => (
                <TicketRow key={t.id} {...t} onOpen={setSelectedTicketId} />
              ))
            ) : (
              <p className="text-sm text-gray-400 px-1 py-6 text-center">
                No tickets logged yet.
              </p>
            )}
          </div>
        </div>
      </main>

      <TicketDetailModal
        ticket={selectedTicket}
        onClose={() => setSelectedTicketId(null)}
      />
    </div>
  );
}