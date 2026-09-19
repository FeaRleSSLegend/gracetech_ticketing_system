// Every hook in lib/ (auth-context, useTickets, useAdmins, useNotifications,
// useComments) calls apiFetch() instead of fetch() directly, and apiFetch()
// is the only place that knows the backend's base URL — set via
// NEXT_PUBLIC_API_URL in .env.local.
//
// Auth is bearer-token only (no cookies/sessions), per the backend docs —
// the token is attached below whenever one's stored.

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "";
const TOKEN_KEY = "itsupport_token";

export function getToken() {
  if (typeof window === "undefined") return null;
  try {
    return localStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
}

export function setToken(token) {
  try {
    if (token) {
      localStorage.setItem(TOKEN_KEY, token);
    } else {
      localStorage.removeItem(TOKEN_KEY);
    }
  } catch {
    // ignore storage errors
  }
}

// --- request wrapper -----------------------------------------------------

const RETRY_COUNT = 6;
const RETRY_DELAY_MS = 7000; // 6 retries * 7s ≈ 42s, covers Render's documented 30-50s cold start

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export async function apiFetch(path, options = {}) {
  const token = getToken();
  const url = `${API_BASE_URL}${path}`;
  const requestInit = {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options.headers || {}),
    },
  };

  let lastNetworkError = null;

  for (let attempt = 0; attempt <= RETRY_COUNT; attempt++) {
    let res;
    try {
      res = await fetch(url, requestInit);
    } catch (err) {
      // This is a network-level failure (server unreachable, connection
      // refused/reset) — exactly what happens while Render's free tier is
      // still spinning up from a cold start. A real CORS misconfiguration
      // also throws this same generic error, so this retries either way —
      // if it's a genuine CORS/config issue, it'll still fail after all
      // retries and surface the real error below.
      lastNetworkError = err;
      if (attempt < RETRY_COUNT) {
        await sleep(RETRY_DELAY_MS);
        continue;
      }
      throw new Error(
        "Couldn't reach the server. It may still be starting up — please try again in a moment."
      );
    }

    const data = await res.json().catch(() => ({}));

    if (!res.ok) {
      // Only treat this as "your session died" if the request actually had
      // a token attached — a 401 from /auth/login with no token yet just
      // means wrong credentials, not an expired session. Gating on `token`
      // keeps those two cases from being conflated.
      if (res.status === 401 && token && typeof window !== "undefined") {
        window.dispatchEvent(new Event("auth:unauthorized"));
      }
      const detailMessage =
        typeof data.detail === "string" ? data.detail : data.detail?.error;
      const message = detailMessage || data.error || data.message || `Request failed (${res.status})`;
      throw new Error(message);
    }

    return data;
  }

  // Unreachable in practice — the loop above always returns or throws —
  // but keeps this function's return type honest for tooling.
  throw lastNetworkError ?? new Error("Request failed");
}