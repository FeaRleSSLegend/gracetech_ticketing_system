"use client";

import Sidebar from "@/components/Sidebar";
import TopBar from "@/components/TopBar";
import { useAuth } from "@/lib/auth-context";
import { useNotifications } from "@/lib/useNotifications";

export default function PortalSettingsPage() {
  const { user } = useAuth();
  const { notifications } = useNotifications(user?.name);
  const myNotificationCount = notifications.filter((n) => n.recipientName !== null).length;

  return (
    <div className="flex flex-col md:flex-row bg-[#F6F7F9] min-h-screen font-sans">
      <Sidebar />
      <main className="flex-1 px-4 py-5 md:px-10 md:py-8">
        <TopBar
          title="Settings"
          notificationCount={myNotificationCount}
          notificationsHref="/portal/notifications"
        />

        <div className="bg-white rounded-2xl border border-gray-100 p-6 max-w-md">
          <h2 className="text-base font-bold text-gray-900 mb-4">Account</h2>
          <div className="space-y-3">
            <div>
              <p className="text-xs text-gray-400 mb-0.5">Name</p>
              <p className="text-sm font-medium text-gray-900">{user.name}</p>
            </div>
            <div>
              <p className="text-xs text-gray-400 mb-0.5">Email</p>
              <p className="text-sm font-medium text-gray-900">
                {user.email}
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}