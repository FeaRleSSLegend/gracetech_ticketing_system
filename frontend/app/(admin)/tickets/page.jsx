"use client";

import { useState } from "react";
import Sidebar from "@/components/Sidebar";
import TopBar from "@/components/TopBar";
import TicketRow from "@/components/TicketRow";
import CreateTicketModal from "@/components/CreateTicketModal";
import TicketDetailModal from "@/components/TicketDetailModal";
import Spinner from "@/components/Spinner";
import { useTickets } from "@/lib/useTickets";
import { useNotifications } from "@/lib/useNotifications";
import { useAuth } from "@/lib/auth-context";

const TABS = [
  { label: "All", value: null },
  { label: "Open", value: "open" },
  { label: "Progress", value: "in_progress" },
  { label: "Resolved", value: "resolved" },
  { label: "Closed", value: "closed" },
];

function StatusTabs({ active, onChange }) {
  return (
    <div className="flex items-center gap-0.5 sm:gap-1 bg-gray-100 rounded-full p-0.5 sm:p-1 mb-6 w-full">
      {TABS.map((tab) => (
        <button
          key={tab.label}
          onClick={() => onChange(tab.value)}
          className={`flex-1 whitespace-nowrap text-center px-2 sm:px-4 py-1 sm:py-1.5 text-[11px] sm:text-sm rounded-full font-medium transition-colors
            ${
              active === tab.value
                ? "bg-white text-gray-900 shadow-sm"
                : "text-gray-500 hover:text-gray-700"
            }`}
        >
          {tab.label}
        </button>
      ))}
    </div>
  );
}

export default function TicketsPage() {
  const { user } = useAuth();
  const { tickets, loading, createTicket, claimTicket, updateTicketStatus, deleteTicket } =
    useTickets();
  const { notifications } = useNotifications(user?.name);
  const [activeStatus, setActiveStatus] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedTicketId, setSelectedTicketId] = useState(null);

  const filtered = activeStatus
    ? tickets.filter((t) => t.status === activeStatus)
    : tickets;

  const selectedTicket = tickets.find((t) => t.id === selectedTicketId) ?? null;

  async function handleCreate({ category, comment, office }) {
    await createTicket({ category, comment, office });
  }

  return (
    <div className="flex flex-col md:flex-row bg-[#F6F7F9] min-h-screen font-sans">
      <Sidebar />
      <main className="flex-1 px-4 py-5 md:px-10 md:py-8">
        <TopBar
          title="Tickets"
          actionLabel="Create Ticket"
          onAction={() => setIsModalOpen(true)}
          notificationCount={notifications.length}
        />

        <div className="bg-white rounded-2xl border border-gray-100 p-3 sm:p-5">
          <StatusTabs active={activeStatus} onChange={setActiveStatus} />

          <div className="space-y-2">
            {loading ? (
              <div className="flex items-center justify-center gap-2 px-1 py-6 text-center text-gray-400 text-sm">
                <Spinner size={16} />
                Loading tickets…
              </div>
            ) : filtered.length > 0 ? (
              filtered.map((t) => (
                <TicketRow key={t.id} {...t} onOpen={setSelectedTicketId} />
              ))
            ) : (
              <p className="text-sm text-gray-400 px-1 py-6 text-center">
                No tickets in this status right now.
              </p>
            )}
          </div>
        </div>
      </main>

      <CreateTicketModal
        open={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onCreate={handleCreate}
      />
      <TicketDetailModal
        ticket={selectedTicket}
        onClose={() => setSelectedTicketId(null)}
        isAdmin
        onClaim={claimTicket}
        onUpdateStatus={updateTicketStatus}
        onDelete={deleteTicket}
      />
    </div>
  );
}