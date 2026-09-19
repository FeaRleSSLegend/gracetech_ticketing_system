"use client";

import { useState } from "react";
import { X } from "lucide-react";
import { CATEGORIES } from "@/data/categories";
import Spinner from "@/components/Spinner";

// onCreate is an async function ({ category, comment, office }) => void,
// wired by the parent page to POST to /api/tickets/.
export default function CreateTicketModal({ open, onClose, onCreate }) {
  const [category, setCategory] = useState(null);
  const [office, setOffice] = useState("");
  const [comment, setComment] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  if (!open) return null;

  const isValid =
    category !== null && office.trim().length > 0 && comment.trim().length > 0;

  function resetAndClose() {
    setCategory(null);
    setOffice("");
    setComment("");
    setError(null);
    setSubmitting(false);
    onClose();
  }

  async function handleSubmit(e) {
    e.preventDefault();
    if (!isValid || submitting) return;

    setSubmitting(true);
    setError(null);
    try {
      await onCreate({ category, comment, office });
      resetAndClose();
    } catch (err) {
      setError(err.message || "Something went wrong creating the ticket");
      setSubmitting(false);
    }
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4"
      onClick={resetAndClose}
    >
      <div
        className="w-full max-w-lg bg-white rounded-2xl border border-gray-100 shadow-xl p-6"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between mb-5">
          <h2 className="text-lg font-bold text-gray-900">Create Ticket</h2>
          <button
            onClick={resetAndClose}
            className="text-gray-400 hover:text-gray-700 transition-colors"
            aria-label="Close"
          >
            <X size={20} strokeWidth={2} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          {/* Category */}
          <div>
            <label className="block text-sm font-semibold text-gray-900 mb-2">
              Category <span className="text-red-500">*</span>
            </label>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
              {CATEGORIES.map((cat) => {
                const Icon = cat.icon;
                const selected = category === cat.key;
                return (
                  <button
                    key={cat.key}
                    type="button"
                    onClick={() => setCategory(cat.key)}
                    className={`flex items-center gap-2 px-3 py-2.5 rounded-xl text-xs font-semibold border transition-colors
                      ${
                        selected
                          ? "bg-red-500 border-red-500 text-white"
                          : "bg-white border-gray-200 text-gray-600 hover:border-gray-300"
                      }`}
                  >
                    <Icon size={15} strokeWidth={2} />
                    {cat.label}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Office */}
          <div>
            <label
              htmlFor="ticket-office"
              className="block text-sm font-semibold text-gray-900 mb-2"
            >
              Office <span className="text-red-500">*</span>
            </label>
            <input
              id="ticket-office"
              type="text"
              value={office}
              onChange={(e) => setOffice(e.target.value)}
              placeholder="e.g. 3rd Floor — East Wing"
              className="w-full rounded-xl border border-gray-200 px-3.5 py-2.5 text-sm text-gray-900 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-red-500/40 focus:border-red-400"
            />
          </div>

          {/* Comment */}
          <div>
            <label
              htmlFor="ticket-comment"
              className="block text-sm font-semibold text-gray-900 mb-2"
            >
              Describe the issue <span className="text-red-500">*</span>
            </label>
            <textarea
              id="ticket-comment"
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              rows={4}
              placeholder="Tell us what's going on..."
              className="w-full rounded-xl border border-gray-200 px-3.5 py-2.5 text-sm text-gray-900 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-red-500/40 focus:border-red-400 resize-none"
            />
          </div>

          {error && <p className="text-xs text-red-500">{error}</p>}

          {/* Actions */}
          <div className="flex items-center justify-end gap-3 pt-1">
            <button
              type="button"
              onClick={resetAndClose}
              className="px-4 py-2.5 rounded-full text-sm font-semibold text-gray-600 hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={!isValid || submitting}
              className="flex items-center gap-2 px-4 py-2.5 rounded-full text-sm font-semibold text-white bg-red-500 hover:bg-red-600 disabled:bg-gray-200 disabled:text-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              {submitting && <Spinner size={14} />}
              {submitting ? "Creating…" : "Create Ticket"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
