"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import AuthShell from "@/components/AuthShell";
import Spinner from "@/components/Spinner";
import { useAuth, consumeSessionExpiredFlag } from "@/lib/auth-context";

export default function LoginPage() {
  const { login } = useAuth();
  const router = useRouter();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [sessionExpired, setSessionExpired] = useState(false);

  // Landing here because a live session expired (not just visiting to log
  // in fresh) — show a clear reason instead of a silent, unexplained redirect.
  useEffect(() => {
    setSessionExpired(consumeSessionExpiredFlag());
  }, []);

  async function handleSubmit(e) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    setSessionExpired(false);
    try {
      const user = await login(email, password);
      router.push(user.role === "admin" ? "/" : "/portal");
    } catch (err) {
      // Login failures are almost always bad credentials — show a clear,
      // consistent message rather than whatever raw text the backend sent
      // (which can vary, or fall back to a generic "Request failed (401)").
      setError("Incorrect login credentials");
      setSubmitting(false);
    }
  }

  return (
    <AuthShell>
      <h1 className="text-xl font-bold text-gray-900 mb-1">Welcome back</h1>
      <p className="text-sm text-gray-400 mb-6">
        Log in to your IT Support account
      </p>

      {sessionExpired && (
        <div className="mb-5 px-3.5 py-2.5 rounded-xl bg-amber-50 border border-amber-100 text-xs text-amber-700">
          Your session expired — please log in again.
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label
            htmlFor="email"
            className="block text-sm font-semibold text-gray-900 mb-1.5"
          >
            Email
          </label>
          <input
            id="email"
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@company.com"
            className="w-full rounded-xl border border-gray-200 px-3.5 py-2.5 text-sm text-gray-900 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-red-500/40 focus:border-red-400"
          />
        </div>

        <div>
          <label
            htmlFor="password"
            className="block text-sm font-semibold text-gray-900 mb-1.5"
          >
            Password
          </label>
          <input
            id="password"
            type="password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
            className="w-full rounded-xl border border-gray-200 px-3.5 py-2.5 text-sm text-gray-900 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-red-500/40 focus:border-red-400"
          />
        </div>

        {error && <p className="text-xs text-red-500">{error}</p>}

        <button
          type="submit"
          disabled={submitting}
          className="w-full flex items-center justify-center gap-2 bg-red-500 hover:bg-red-600 disabled:bg-gray-200 disabled:text-gray-400 text-white text-sm font-semibold py-2.5 rounded-full transition-colors"
        >
          {submitting && <Spinner size={15} />}
          {submitting ? "Logging in…" : "Log in"}
        </button>
      </form>

      <p className="text-xs text-gray-400 mt-5 text-center">
        Don't have an account?{" "}
        <Link href="/signup" className="text-red-600 font-semibold">
          Sign up
        </Link>
      </p>
    </AuthShell>
  );
}