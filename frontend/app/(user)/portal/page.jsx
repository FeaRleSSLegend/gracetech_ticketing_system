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

export default function PortalDashboardPage() {
  const { user } = useAuth();
  const { tickets, loading, createTicket } = useTickets();
  const { notifications } = useNotifications(user?.name);
  const myNotificationCount = notifications.filter((n) => n.recipientName !== null).length;
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedTicketId, setSelectedTicketId] = useState(null);

  const myTickets = tickets.filter((t) => t.createdBy === user.name);
  const recent = myTickets.slice(0, 5);
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
          notificationCount={myNotificationCount}
          notificationsHref="/portal/notifications"
        />

        <div className="bg-white rounded-2xl border border-gray-100 p-5">
          <div className="flex items-center justify-between mb-4 px-1">
            <h2 className="text-base font-bold text-gray-900">
              My Tickets
            </h2>
          </div>

          <div className="space-y-2">
            {loading ? (
              <div className="flex items-center justify-center gap-2 px-1 py-6 text-center text-gray-400 text-sm">
                <Spinner size={16} />
                Loading tickets…
              </div>
            ) : recent.length > 0 ? (
              recent.map((t) => (
                <TicketRow key={t.id} {...t} onOpen={setSelectedTicketId} />
              ))
            ) : (
              <p className="text-sm text-gray-400 px-1 py-6 text-center">
                You haven't submitted any tickets yet.
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
      />
    </div>
  );
}