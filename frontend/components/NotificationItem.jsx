import { getCategory } from "@/data/categories";
import { formatDateTime } from "@/lib/formatDate";

// kind: "new_ticket" (broadcast — a user submitted a ticket),
// "claimed" (broadcast — an admin claimed a ticket, whole team sees it),
// "resolved" / "closed" (targeted — the employee who filed it is told).
export default function NotificationItem({ kind, actorName, category, comment, time }) {
  const cat = getCategory(category);
  const Icon = cat.icon;

  const messageByKind = {
    new_ticket: (
      <>
        <span className="font-semibold">{actorName}</span> submitted a new{" "}
        <span className="font-semibold text-red-600">{cat.label}</span> ticket
      </>
    ),
    claimed: (
      <>
        <span className="font-semibold">{actorName}</span> claimed a{" "}
        <span className="font-semibold text-red-600">{cat.label}</span> ticket
      </>
    ),
    resolved: (
      <>
        <span className="font-semibold">{actorName}</span> marked your{" "}
        <span className="font-semibold text-red-600">{cat.label}</span> ticket
        resolved
      </>
    ),
    closed: (
      <>
        <span className="font-semibold">{actorName}</span> closed your{" "}
        <span className="font-semibold text-red-600">{cat.label}</span> ticket
      </>
    ),
  };

  return (
    <div className="flex items-start gap-4 px-5 py-4 rounded-2xl bg-red-50/40 hover:bg-red-50/70 transition-colors">
      <div className="w-11 h-11 rounded-xl bg-red-100 flex items-center justify-center shrink-0">
        <Icon size={19} className="text-red-600" strokeWidth={2} />
      </div>

      <div className="min-w-0 flex-1">
        <p className="text-sm text-gray-900">
          {messageByKind[kind] ?? messageByKind.new_ticket}
        </p>
        <p className="text-xs text-gray-400 mt-0.5 truncate">{comment}</p>
      </div>

      <span className="text-xs text-gray-400 whitespace-nowrap shrink-0 pt-0.5">
        {formatDateTime(time)}
      </span>
    </div>
  );
}
