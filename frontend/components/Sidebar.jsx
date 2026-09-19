"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  Headphones,
  LayoutDashboard,
  Ticket,
  History,
  Settings,
  LogOut,
  Menu,
  X,
} from "lucide-react";
import { useAuth } from "@/lib/auth-context";

function navItemsForRole(role) {
  if (role === "admin") {
    return [
      { label: "Dashboard", icon: LayoutDashboard, path: "/", exact: true },
      { label: "Tickets", icon: Ticket, path: "/tickets", exact: false },
      { label: "History", icon: History, path: "/history", exact: false },
    ];
  }
  return [
    { label: "Dashboard", icon: LayoutDashboard, path: "/portal", exact: true },
    { label: "Tickets", icon: Ticket, path: "/portal/tickets", exact: false },
    { label: "History", icon: History, path: "/portal/history", exact: false },
  ];
}

function settingsPathForRole(role) {
  return role === "admin" ? "/settings" : "/portal/settings";
}

function NavItem({ icon: Icon, label, path, isActive, onNavigate }) {
  return (
    <Link
      href={path}
      onClick={onNavigate}
      className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm font-medium transition-colors
        ${
          isActive
            ? "bg-red-500 text-white"
            : "text-gray-500 hover:bg-gray-50 hover:text-gray-900"
        }`}
    >
      <Icon size={18} strokeWidth={2} />
      <span>{label}</span>
    </Link>
  );
}

export default function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const { user, logout } = useAuth();
  const [mobileOpen, setMobileOpen] = useState(false);

  // Close the mobile drawer automatically whenever the route changes —
  // otherwise it stays open after tapping a nav link.
  useEffect(() => {
    setMobileOpen(false);
  }, [pathname]);

  // Guarded layouts should prevent this from ever rendering without a user,
  // but bail out gracefully just in case.
  if (!user) return null;

  const navItems = navItemsForRole(user.role);
  const settingsPath = settingsPathForRole(user.role);
  const settingsActive = pathname === settingsPath;
  const initial = user.name?.charAt(0)?.toUpperCase() ?? "?";

  function handleLogout() {
    logout();
    router.push("/login");
  }

  const sidebarContent = (
    <>
      <div>
        {/* Brand */}
        <div className="px-6 pt-7 pb-6 flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-gray-900 flex items-center justify-center">
            <Headphones size={17} className="text-white" strokeWidth={2} />
          </div>
          <span className="text-[15px] font-bold text-gray-900 tracking-tight">
            IT Support
          </span>
        </div>

        {/* Nav */}
        <div className="px-4">
          <p className="px-3 mb-2 text-[11px] font-semibold tracking-wider text-gray-400 uppercase">
            Overview
          </p>
          <nav className="space-y-1">
            {navItems.map((item) => (
              <NavItem
                key={item.label}
                {...item}
                isActive={
                  item.exact ? pathname === item.path : pathname.startsWith(item.path)
                }
                onNavigate={() => setMobileOpen(false)}
              />
            ))}
          </nav>
        </div>
      </div>

      {/* Footer: settings + profile */}
      <div className="px-4 pb-5">
        <Link
          href={settingsPath}
          onClick={() => setMobileOpen(false)}
          className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm font-medium transition-colors mb-3
            ${
              settingsActive
                ? "bg-red-500 text-white"
                : "text-gray-500 hover:bg-gray-50 hover:text-gray-900"
            }`}
        >
          <Settings size={18} strokeWidth={2} />
          <span>Settings</span>
        </Link>
        <div className="border-t border-gray-100 pt-4 px-1 flex items-center gap-3">
          <div className="w-9 h-9 rounded-full bg-red-50 text-red-600 flex items-center justify-center text-sm font-semibold shrink-0">
            {initial}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-semibold text-gray-900 leading-tight truncate">
              {user.name}
            </p>
            <p className="text-xs text-gray-400 leading-tight truncate">
              {user.email}
            </p>
          </div>
          <button
            onClick={handleLogout}
            className="text-gray-400 hover:text-gray-700 transition-colors shrink-0"
            aria-label="Log out"
          >
            <LogOut size={17} strokeWidth={2} />
          </button>
        </div>
      </div>
    </>
  );

  return (
    <>
      {/* Mobile top bar: hamburger + brand mark, only below md */}
      <div className="md:hidden sticky top-0 z-30 flex items-center gap-3 px-4 h-14 bg-white border-b border-gray-100">
        <button
          onClick={() => setMobileOpen(true)}
          className="text-gray-500 hover:text-gray-900 transition-colors"
          aria-label="Open menu"
        >
          <Menu size={22} strokeWidth={2} />
        </button>
        <div className="w-7 h-7 rounded-lg bg-gray-900 flex items-center justify-center">
          <Headphones size={14} className="text-white" strokeWidth={2} />
        </div>
        <span className="text-sm font-bold text-gray-900 tracking-tight">
          IT Support
        </span>
      </div>

      {/* Backdrop, mobile only, shown while the drawer is open */}
      {mobileOpen && (
        <div
          onClick={() => setMobileOpen(false)}
          className="md:hidden fixed inset-0 z-40 bg-black/40"
          aria-hidden="true"
        />
      )}

      {/* Sidebar itself — sticky in the desktop flex row, staying pinned in
          the viewport while <main> scrolls past it. A fixed off-canvas
          drawer on mobile that slides in/out. */}
      <aside
        className={`fixed inset-y-0 left-0 z-50 w-64 bg-white border-r border-gray-100 flex flex-col justify-between overflow-y-auto
          transform transition-transform duration-200
          md:sticky md:top-0 md:z-auto md:h-screen md:shrink-0 md:translate-x-0
          ${mobileOpen ? "translate-x-0" : "-translate-x-full"}`}
      >
        {/* Close button, mobile only, top-right of the open drawer */}
        <button
          onClick={() => setMobileOpen(false)}
          className="md:hidden absolute top-4 right-4 text-gray-400 hover:text-gray-700 transition-colors"
          aria-label="Close menu"
        >
          <X size={20} strokeWidth={2} />
        </button>
        {sidebarContent}
      </aside>
    </>
  );
}