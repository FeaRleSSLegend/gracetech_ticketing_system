"use client";

import { useState } from "react";
import { X, Check, CircleCheck, CircleX, Send, Trash2 } from "lucide-react";
import { STATUS_STYLES } from "@/data/tickets";
import { getCategory } from "@/data/categories";
import { formatDateTime } from "@/lib/formatDate";
import { useComments } from "@/lib/useComments";
import { useAdmins } from "@/lib/useAdmins";
import { useAuth } from "@/lib/auth-context";
import Spinner from "@/components/Spinner";

// isAdmin controls whether Claim/Resolve/Close/Delete actions render at
// all. onClaim(ticketId) and onUpdateStatus(ticketId, "resolved" | "closed")
// are async — errors (e.g. 409 already claimed) are caught and shown inline.
// onDelete(ticketId) is also async — the modal closes automatically once
// it resolves (see handleDelete below).
export default function TicketDetailModal({
  ticket,
  onClose,
  isAdmin = false,
  onClaim,
  onUpdateStatus,
  onDelete,
}) {
  const [actionError, setActionError] = useState(null);
  const [actionLoading, setActionLoading] = useState(false);
  const [commentText, setCommentText] = useState("");
  const [commentError, setCommentError] = useState(null);
  const [postingComment, setPostingComment] = useState(false);
  const [confirmingDelete, setConfirmingDelete] = useState(false);
  const [deleting, setDeleting] = useState(false);

  const { comments, loading: commentsLoading, addComment } = useComments(ticket?.id);
  const { user } = useAuth();
  const { admins } = useAdmins();

  if (!ticket) return null;

  const s = STATUS_STYLES[ticket.status];
  const cat = getCategory(ticket.category);
  const CategoryIcon = cat.icon;

  // The comments API only returns a numeric user_id, not a name — resolve
  // it against data we already have: the logged-in user (for "You"), the
  // admins list (for any admin's comment), and otherwise fall back to the
  // ticket's creator, since only the ticket owner and admins can comment.
  function nameForComment(comment) {
    if (user?.id != null && String(comment.user_id) === String(user.id)) {
      return "You";
    }
    const admin = admins.find((a) => String(a.id) === String(comment.user_id));
    if (admin) return admin.name;
    if (ticket.createdBy) return ticket.createdBy;
    return "Someone";
  }

  async function handleDelete() {
    if (!onDelete || deleting) return;
    if (!confirmingDelete) {
      setConfirmingDelete(true);
      return;
    }
    setDeleting(true);
    setActionError(null);
    try {
      await onDelete(ticket.id);
      onClose();
    } catch (err) {
      setActionError(err.message);
      setDeleting(false);
      setConfirmingDelete(false);
    }
  }

  async function handleClaim() {
    if (!onClaim || actionLoading) return;
    setActionLoading(true);
    setActionError(null);
    try {
      await onClaim(ticket.id);
    } catch (err) {
      setActionError(err.message);
    } finally {
      setActionLoading(false);
    }
  }

  async function handleUpdateStatus(status) {
    if (!onUpdateStatus || actionLoading) return;
    setActionLoading(true);
    setActionError(null);
    try {
      await onUpdateStatus(ticket.id, status);
    } catch (err) {
      setActionError(err.message);
    } finally {
      setActionLoading(false);
    }
  }

  async function handlePostComment(e) {
    e.preventDefault();
    if (!commentText.trim() || postingComment) return;
    setPostingComment(true);
    setCommentError(null);
    try {
      await addComment(commentText.trim());
      setCommentText("");
    } catch (err) {
      setCommentError(err.message);
    } finally {
      setPostingComment(false);
    }
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4"
      onClick={onClose}
    >
      <div
        className="w-full max-w-lg bg-white rounded-2xl border border-gray-100 shadow-xl p-6 max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-start justify-between mb-5">
          <div className="flex items-center gap-3">
            <div className="w-11 h-11 rounded-xl bg-red-100 flex items-center justify-center shrink-0">
              <CategoryIcon size={19} className="text-red-600" strokeWidth={2} />
            </div>
            <div>
              <p className="text-base font-bold text-gray-900">{cat.label}</p>
              <div className="flex items-center gap-1.5 mt-0.5">
                <span className={`w-2 h-2 rounded-full ${s.dot}`} />
                <span className={`text-xs font-medium ${s.text}`}>{s.label}</span>
              </div>
            </div>
          </div>
          <div className="flex items-center gap-3 shrink-0">
            {isAdmin && onDelete && (
              <button
                onClick={handleDelete}
                disabled={deleting}
                className={`transition-colors ${
                  confirmingDelete
                    ? "text-red-600 hover:text-red-700"
                    : "text-gray-400 hover:text-red-600"
                }`}
                aria-label={confirmingDelete ? "Confirm delete" : "Delete ticket"}
                title={confirmingDelete ? "Click again to confirm" : "Delete ticket"}
              >
                {deleting ? <Spinner size={18} /> : <Trash2 size={18} strokeWidth={2} />}
              </button>
            )}
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-700 transition-colors"
              aria-label="Close"
            >
              <X size={20} strokeWidth={2} />
            </button>
          </div>
        </div>

        {confirmingDelete && (
          <div className="mb-4 -mt-2 flex items-center justify-between gap-3 px-3.5 py-2.5 rounded-xl bg-red-50 border border-red-100">
            <p className="text-xs text-red-700">
              Delete this ticket permanently? This can't be undone.
            </p>
            <button
              onClick={() => setConfirmingDelete(false)}
              className="text-xs font-semibold text-gray-500 hover:text-gray-700 shrink-0"
            >
              Cancel
            </button>
          </div>
        )}

        <div className="space-y-4">
          <div>
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">
              Description
            </p>
            <p className="text-sm text-gray-900">{ticket.comment}</p>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">
                Office
              </p>
              <p className="text-sm text-gray-900">{ticket.office || "—"}</p>
            </div>
            <div>
              <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">
                Submitted by
              </p>
              <p className="text-sm text-gray-900">{ticket.createdBy}</p>
            </div>
            <div>
              <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">
                Time
              </p>
              <p className="text-sm text-gray-900">{formatDateTime(ticket.time)}</p>
            </div>
            <div>
              <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">
                Claimed by
              </p>
              <p className="text-sm text-gray-900">
                {ticket.assignedTo || "Unclaimed"}
              </p>
            </div>
            {ticket.closedOn && (
              <div>
                <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">
                  Closed on
                </p>
                <p className="text-sm text-gray-900">
                  {formatDateTime(ticket.closedOn)}
                </p>
              </div>
            )}
          </div>

          {/* Comments */}
          <div className="pt-2 border-t border-gray-100">
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2 pt-3">
              Comments
            </p>

            <div className="space-y-2 max-h-48 overflow-y-auto mb-3">
              {commentsLoading ? (
                <div className="flex items-center gap-2 text-xs text-gray-400">
                  <Spinner size={13} />
                  Loading comments…
                </div>
              ) : comments.length > 0 ? (
                comments.map((c) => (
                  <div key={c.id} className="bg-gray-50 rounded-xl px-3.5 py-2.5">
                    <div className="flex items-center justify-between mb-0.5">
                      <span className="text-xs font-semibold text-gray-900">
                        {nameForComment(c)}
                      </span>
                      <span className="text-[11px] text-gray-400">
                        {formatDateTime(c.time || c.created_at || c.createdAt)}
                      </span>
                    </div>
                    <p className="text-sm text-gray-700">{c.body}</p>
                  </div>
                ))
              ) : (
                <p className="text-xs text-gray-400">No comments yet.</p>
              )}
            </div>

            <form onSubmit={handlePostComment} className="flex items-center gap-2">
              <input
                type="text"
                value={commentText}
                onChange={(e) => setCommentText(e.target.value)}
                placeholder="Add a comment…"
                className="flex-1 rounded-full border border-gray-200 px-3.5 py-2 text-sm text-gray-900 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-red-500/40 focus:border-red-400"
              />
              <button
                type="submit"
                disabled={!commentText.trim() || postingComment}
                className="shrink-0 w-9 h-9 flex items-center justify-center rounded-full bg-red-500 hover:bg-red-600 disabled:bg-gray-200 disabled:text-gray-400 text-white transition-colors"
                aria-label="Post comment"
              >
                {postingComment ? <Spinner size={15} /> : <Send size={15} strokeWidth={2} />}
              </button>
            </form>
            {commentError && (
              <p className="text-xs text-red-500 mt-1.5">{commentError}</p>
            )}
          </div>

          {/* Actions — admins only */}
          {isAdmin && (
            <div className="pt-2 border-t border-gray-100">
              {actionError && (
                <p className="text-xs text-red-500 mb-2">{actionError}</p>
              )}

              {ticket.status === "open" && (
                <button
                  type="button"
                  onClick={handleClaim}
                  disabled={actionLoading}
                  className="w-full flex items-center justify-center gap-2 bg-red-500 hover:bg-red-600 disabled:bg-gray-200 disabled:text-gray-400 text-white text-sm font-semibold py-2.5 rounded-full transition-colors"
                >
                  {actionLoading ? (
                    <Spinner size={16} />
                  ) : (
                    <Check size={16} strokeWidth={2.5} />
                  )}
                  {actionLoading ? "Claiming…" : "Claim Ticket"}
                </button>
              )}

              {ticket.status === "in_progress" && (
                <div className="flex items-center gap-3">
                  <button
                    type="button"
                    onClick={() => handleUpdateStatus("resolved")}
                    disabled={actionLoading}
                    className="flex-1 flex items-center justify-center gap-2 bg-emerald-500 hover:bg-emerald-600 disabled:bg-gray-200 disabled:text-gray-400 text-white text-sm font-semibold py-2.5 rounded-full transition-colors"
                  >
                    {actionLoading ? (
                      <Spinner size={16} />
                    ) : (
                      <CircleCheck size={16} strokeWidth={2.5} />
                    )}
                    {actionLoading ? "Working…" : "Mark Resolved"}
                  </button>
                  <button
                    type="button"
                    onClick={() => handleUpdateStatus("closed")}
                    disabled={actionLoading}
                    className="flex-1 flex items-center justify-center gap-2 bg-gray-100 hover:bg-gray-200 disabled:bg-gray-50 disabled:text-gray-300 text-gray-700 text-sm font-semibold py-2.5 rounded-full transition-colors"
                  >
                    {actionLoading ? (
                      <Spinner size={16} />
                    ) : (
                      <CircleX size={16} strokeWidth={2.5} />
                    )}
                    {actionLoading ? "Working…" : "Close"}
                  </button>
                </div>
              )}

              {(ticket.status === "resolved" || ticket.status === "closed") && (
                <div className="flex items-center gap-2 text-sm font-semibold pt-1 text-gray-500">
                  <Check size={16} strokeWidth={2.5} />
                  {ticket.status === "resolved" ? "Resolved" : "Closed"}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}