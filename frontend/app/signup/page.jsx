"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import AuthShell from "@/components/AuthShell";
import Spinner from "@/components/Spinner";
import { useAuth } from "@/lib/auth-context";

export default function SignupPage() {
  const { signup } = useAuth();
  const router = useRouter();

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      // Signups always come out as an "employee" account — there is no role
      // selector here, and the /api/auth/register endpoint enforces this
      // server-side too, so this can't be bypassed from the client.
      await signup(name, email, password);
      router.push("/portal");
    } catch (err) {
      setError(err.message);
      setSubmitting(false);
    }
  }

  return (
    <AuthShell>
      <h1 className="text-xl font-bold text-gray-900 mb-1">Create an account</h1>
      <p className="text-sm text-gray-400 mb-6">
        Sign up to submit and track your support tickets
      </p>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label
            htmlFor="name"
            className="block text-sm font-semibold text-gray-900 mb-1.5"
          >
            Full name
          </label>
          <input
            id="name"
            type="text"
            required
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Jane Doe"
            className="w-full rounded-xl border border-gray-200 px-3.5 py-2.5 text-sm text-gray-900 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-red-500/40 focus:border-red-400"
          />
        </div>

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
          {submitting ? "Creating account…" : "Sign up"}
        </button>
      </form>

      <p className="text-xs text-gray-400 mt-5 text-center">
        Already have an account?{" "}
        <Link href="/login" className="text-red-600 font-semibold">
          Log in
        </Link>
      </p>
    </AuthShell>
  );
}
