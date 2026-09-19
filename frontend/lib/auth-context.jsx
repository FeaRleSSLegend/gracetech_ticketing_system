"use client";

import { createContext, useCallback, useContext, useEffect, useRef, useState } from "react";
import { apiFetch, setToken, getToken } from "@/lib/api";

const AuthContext = createContext(null);
const STORAGE_KEY = "itsupport_auth_user";
const EXPIRED_FLAG_KEY = "itsupport_session_expired";

// Reads the `exp` claim out of a JWT's payload (base64url-encoded middle
// segment) and returns it as a millisecond timestamp. Returns null if the
// token isn't a JWT or has no exp claim, so callers can fall back gracefully.
function getTokenExpiryMs(token) {
  try {
    const payload = token.split(".")[1];
    const json = atob(payload.replace(/-/g, "+").replace(/_/g, "/"));
    const decoded = JSON.parse(json);
    return decoded.exp ? decoded.exp * 1000 : null;
  } catch {
    return null;
  }
}

// Read by the login page to show "your session expired" instead of a
// generic redirect with no explanation.
export function consumeSessionExpiredFlag() {
  try {
    const wasExpired = localStorage.getItem(EXPIRED_FLAG_KEY) === "1";
    localStorage.removeItem(EXPIRED_FLAG_KEY);
    return wasExpired;
  } catch {
    return false;
  }
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const logoutTimerRef = useRef(null);

  const clearLogoutTimer = useCallback(() => {
    if (logoutTimerRef.current) {
      clearTimeout(logoutTimerRef.current);
      logoutTimerRef.current = null;
    }
  }, []);

  const persist = useCallback((nextUser) => {
    setUser(nextUser);
    try {
      if (nextUser) {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(nextUser));
      } else {
        localStorage.removeItem(STORAGE_KEY);
      }
    } catch {
      // ignore storage errors
    }
  }, []);

  const logout = useCallback(
    (opts = {}) => {
      clearLogoutTimer();
      setToken(null);
      persist(null);
      if (opts.expired) {
        try {
          localStorage.setItem(EXPIRED_FLAG_KEY, "1");
        } catch {
          // ignore storage errors
        }
      }
    },
    [persist, clearLogoutTimer]
  );

  // Schedules an automatic logout for the exact moment the current token
  // expires, instead of waiting for the user to notice broken requests.
  const scheduleAutoLogout = useCallback(
    (token) => {
      clearLogoutTimer();
      const expiryMs = getTokenExpiryMs(token);
      if (!expiryMs) return; // not a JWT / no exp claim — nothing to schedule

      const msUntilExpiry = expiryMs - Date.now();
      if (msUntilExpiry <= 0) {
        logout({ expired: true });
        return;
      }
      logoutTimerRef.current = setTimeout(() => {
        logout({ expired: true });
      }, msUntilExpiry);
    },
    [logout, clearLogoutTimer]
  );

  // Restore session on load. If the stored token already expired while the
  // tab/browser was closed, don't restore it — log out immediately instead.
  useEffect(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      const token = getToken();
      if (stored && token) {
        const expiryMs = getTokenExpiryMs(token);
        if (expiryMs && expiryMs <= Date.now()) {
          setToken(null);
          localStorage.removeItem(STORAGE_KEY);
          localStorage.setItem(EXPIRED_FLAG_KEY, "1");
        } else {
          setUser(JSON.parse(stored));
          scheduleAutoLogout(token);
        }
      }
    } catch {
      // ignore malformed/unavailable storage
    }
    setLoading(false);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Safety net: if ANY authenticated request anywhere in the app comes back
  // 401, the token is no longer valid for some reason (expired early,
  // revoked, clock drift vs. our own scheduled timer, etc.) — log out
  // globally rather than leaving the user stuck watching requests fail.
  // lib/api.js dispatches this event; see the note there for why it only
  // fires for requests that actually carried a token (not failed logins).
  useEffect(() => {
    function handleUnauthorized() {
      logout({ expired: true });
    }
    window.addEventListener("auth:unauthorized", handleUnauthorized);
    return () => window.removeEventListener("auth:unauthorized", handleUnauthorized);
  }, [logout]);

  // Checks a few common field names for the auth token — the documented
  // shape uses "token", but FastAPI/OAuth2 backends very commonly return
  // "access_token" instead. Trying both makes this resilient regardless of
  // which convention the real backend actually uses.
  const extractToken = (data) => data.token || data.access_token || data.accessToken;

  const login = useCallback(
    async (email, password) => {
      const data = await apiFetch("/api/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });
      const token = extractToken(data);
      if (token) {
        setToken(token);
        scheduleAutoLogout(token);
      }
      persist(data.user);
      return data.user;
    },
    [persist, scheduleAutoLogout]
  );

  // Every signup comes back as role: "employee" — enforced server-side
  // regardless of anything the client sends.
  const signup = useCallback(
    async (name, email, password) => {
      const data = await apiFetch("/api/auth/register", {
        method: "POST",
        body: JSON.stringify({ name, email, password }),
      });
      const token = extractToken(data);
      if (token) {
        setToken(token);
        scheduleAutoLogout(token);
      }
      persist(data.user);
      return data.user;
    },
    [persist, scheduleAutoLogout]
  );

  return (
    <AuthContext.Provider value={{ user, loading, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
  return ctx;
}