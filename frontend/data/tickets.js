// Status → color/label mapping used by TicketRow and TicketDetailModal.
// Matches the real backend's 4-state model (open/in_progress/resolved/closed).
export const STATUS_STYLES = {
  open: { dot: "bg-red-500", label: "Open", text: "text-red-600" },
  in_progress: { dot: "bg-amber-500", label: "In Progress", text: "text-amber-600" },
  resolved: { dot: "bg-emerald-500", label: "Resolved", text: "text-emerald-600" },
  closed: { dot: "bg-gray-300", label: "Closed", text: "text-gray-400" },
};
