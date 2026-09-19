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

function TicketsCard({ tickets, loading, onOpen }) {
  const recent = tickets.slice(0, 5);

  return (
    <div className="bg-white rounded-2xl border border-gray-100 p-5">
      <div className="flex items-center justify-between mb-4 px-1">
        <h2 className="text-base font-bold text-gray-900">My Claimed Tickets</h2>
        <span className="text-xs text-gray-400">{tickets.length} total</span>
      </div>

      <div className="space-y-2">
        {loading ? (
          <div className="flex items-center justify-center gap-2 px-1 py-6 text-center text-gray-400 text-sm">
                <Spinner size={16} />
                Loading tickets…
              </div>
        ) : recent.length > 0 ? (
          recent.map((t) => <TicketRow key={t.id} {...t} onOpen={onOpen} />)
        ) : (
          <p className="text-sm text-gray-400 px-1 py-6 text-center">
            You haven't claimed any tickets yet — head to Tickets to claim one.
          </p>
        )}
      </div>
    </div>
  );
}

export default function DashboardPage() {
  const { user } = useAuth();
  const { tickets, loading, createTicket, claimTicket, updateTicketStatus, deleteTicket } =
    useTickets();
  const { notifications } = useNotifications(user?.name);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedTicketId, setSelectedTicketId] = useState(null);

  const myTickets = tickets.filter((t) => t.assignedTo === user?.name);
  const selectedTicket = tickets.find((t) => t.id === selectedTicketId) ?? null;

  async function handleCreate({ category, comment, office }) {
    await createTicket({ category, comment, office });
  }

  return (
    <div className="flex flex-col md:flex-row bg-[#F6F7F9] min-h-screen font-sans">
      <Sidebar />
      <main className="flex-1 px-4 py-5 md:px-10 md:py-8">
        <TopBar
          title="Dashboard"
          actionLabel="Create Ticket"
          onAction={() => setIsModalOpen(true)}
          notificationCount={notifications.length}
        />
        <TicketsCard
          tickets={myTickets}
          loading={loading}
          onOpen={setSelectedTicketId}
        />
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