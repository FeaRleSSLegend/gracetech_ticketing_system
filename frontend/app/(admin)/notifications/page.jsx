"use client";

import Sidebar from "@/components/Sidebar";
import TopBar from "@/components/TopBar";
import NotificationItem from "@/components/NotificationItem";
import Spinner from "@/components/Spinner";
import { useNotifications } from "@/lib/useNotifications";
import { useAuth } from "@/lib/auth-context";

export default function NotificationsPage() {
  const { user } = useAuth();
  const { notifications, loading } = useNotifications(user?.name);

  return (
    <div className="flex flex-col md:flex-row bg-[#F6F7F9] min-h-screen font-sans">
      <Sidebar />
      <main className="flex-1 px-4 py-5 md:px-10 md:py-8">
        <TopBar title="Notifications" notificationCount={notifications.length} />

        <div className="bg-white rounded-2xl border border-gray-100 p-5">
          <div className="flex items-center justify-between mb-4 px-1">
            <h2 className="text-base font-bold text-gray-900">Activity</h2>
            <span className="text-xs text-gray-400">
              {notifications.length} total
            </span>
          </div>

          <div className="space-y-2">
            {loading ? (
              <div className="flex items-center justify-center gap-2 px-1 py-6 text-center text-gray-400 text-sm">
                <Spinner size={16} />
                Loading…
              </div>
            ) : notifications.length > 0 ? (
              notifications.map((n) => <NotificationItem key={n.id} {...n} />)
            ) : (
              <p className="text-sm text-gray-400 px-1 py-6 text-center">
                No notifications right now.
              </p>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}