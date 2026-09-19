"use client";

import Link from "next/link";
import { Bell, Plus } from "lucide-react";

// actionLabel is optional — pages like History that don't need a primary
// action can omit it and only the title (+ bell) will render.
// notificationCount renders a small badge on the bell when > 0.
// showBell hides the bell entirely. notificationsHref lets each section
// (admin vs. user portal) point the bell at its own notifications route.
export default function TopBar({
  title,
  actionLabel,
  onAction,
  notificationCount = 0,
  showBell = true,
  notificationsHref = "/notifications",
}) {
  return (
    <div className="flex items-center justify-between mb-5 md:mb-8">
      <h1 className="text-xl md:text-2xl font-bold text-gray-900 tracking-tight">
        {title}
      </h1>
      <div className="flex items-center gap-3 md:gap-4">
        {showBell && (
          <Link
            href={notificationsHref}
            className="relative text-gray-400 hover:text-gray-700 transition-colors shrink-0"
            aria-label="Notifications"
          >
            <Bell size={20} strokeWidth={2} />
            {notificationCount > 0 && (
              <span className="absolute -top-1.5 -right-1.5 min-w-[16px] h-4 px-1 rounded-full bg-red-500 text-white text-[10px] font-semibold flex items-center justify-center ring-2 ring-white">
                {notificationCount}
              </span>
            )}
          </Link>
        )}
        {actionLabel && (
          <button
            onClick={onAction}
            aria-label={actionLabel}
            className="flex items-center gap-1.5 bg-red-500 hover:bg-red-600 text-white text-sm font-semibold px-3.5 sm:px-4 py-2.5 rounded-full transition-colors shrink-0"
          >
            <Plus size={16} strokeWidth={2.5} />
            <span className="hidden sm:inline">{actionLabel}</span>
          </button>
        )}
      </div>
    </div>
  );
}