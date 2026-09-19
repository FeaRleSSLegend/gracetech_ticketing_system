"use client";

import { STATUS_STYLES } from "@/data/tickets";
import { getCategory } from "@/data/categories";
import { formatDateTime } from "@/lib/formatDate";

// A ticket row is purely informational — category icon, title/comment,
// status, and a trailing time/closedOn. Clicking anywhere on it opens the
// detail modal (onOpen), where the "Mark Done" action actually lives.
//
// Mobile (below sm): stacks into a small card — icon + category + status on
// one line, the full comment wrapping below it (not truncated), then the
// time. Desktop (sm and up): the original single-row layout.
export default function TicketRow({
  id,
  category,
  comment,
  status,
  time,
  closedOn,
  onOpen,
}) {
  const s = STATUS_STYLES[status];
  const cat = getCategory(category);
  const CategoryIcon = cat.icon;

  return (
    <div
      onClick={onOpen ? () => onOpen(id) : undefined}
      className={`flex flex-col sm:flex-row sm:items-center gap-2.5 sm:gap-4 px-3.5 sm:px-5 py-3 sm:py-4 rounded-2xl bg-red-50/40 hover:bg-red-50/70 transition-colors ${
        onOpen ? "cursor-pointer" : ""
      }`}
    >
      <div className="flex items-center gap-3 sm:flex-1 sm:min-w-0">
        {/* Category icon */}
        <div className="w-9 h-9 sm:w-11 sm:h-11 rounded-xl bg-red-100 flex items-center justify-center shrink-0">
          <CategoryIcon
            className="w-4 h-4 sm:w-[19px] sm:h-[19px] text-red-600"
            strokeWidth={2}
          />
        </div>

        {/* Mobile: category label + status inline with the icon */}
        <div className="min-w-0 flex-1 flex items-center justify-between gap-2 sm:hidden">
          <p className="text-sm font-semibold text-red-600 truncate">
            {cat.label}
          </p>
          <div className="flex items-center gap-1.5 shrink-0">
            <span className={`w-2 h-2 rounded-full ${s.dot}`} />
            <span className={`text-xs font-medium ${s.text}`}>{s.label}</span>
          </div>
        </div>

        {/* Desktop: category label + comment, stacked together */}
        <div className="hidden sm:block min-w-0 flex-1">
          <p className="text-sm font-semibold text-red-600 truncate">
            {cat.label}
          </p>
          <p className="text-xs text-gray-400 truncate">{comment}</p>
        </div>
      </div>

      {/* Mobile: full comment, wraps up to 2 lines instead of truncating */}
      <p className="text-xs text-gray-500 leading-relaxed line-clamp-2 pl-12 -mt-1 sm:hidden">
        {comment}
      </p>

      {/* Desktop: status as its own column */}
      <div className="hidden sm:flex items-center gap-1.5 shrink-0 w-28">
        <span className={`w-2 h-2 rounded-full ${s.dot}`} />
        <span className={`text-xs font-medium ${s.text}`}>{s.label}</span>
      </div>

      {/* Trailing meta */}
      <div className="pl-12 sm:pl-0 sm:shrink-0 sm:w-28 sm:text-right">
        <span className="text-[11px] sm:text-xs text-gray-400 whitespace-nowrap">
          {closedOn ? `Closed ${formatDateTime(closedOn)}` : formatDateTime(time)}
        </span>
      </div>
    </div>
  );
}