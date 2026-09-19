# IT Support Dashboard

A ticket management system with two experiences — an **Admin dashboard** and an **Employee portal** — built with Next.js (App Router), Tailwind CSS, and lucide-react. Connected to the real **GraceTech Ticketing API**.

## Getting started

```bash
npm install
npm run dev
```

Open `http://localhost:3000`.

**Heads up:** the backend runs on a free-tier Render instance. The first request after inactivity can take 30–50 seconds to respond while it spins back up — that's expected, not a bug, if a page looks stuck on "Loading…" right after opening the app.

There are no seeded demo accounts here — sign up through `/signup` to create an employee account, or ask whoever has backend access to create/confirm an admin account for you (there's no public way to self-register as admin, by design).

## How it works

- **One login page** (`/login`) for everyone. The account's `role` (`"employee"` or `"admin"`) decides where you land after login: admin → `/` (Admin Dashboard), employee → `/portal`.
- **Signup is employee-only** — `/signup` has no role field, and the backend forces `role: "employee"` server-side regardless of anything sent, so it can't be bypassed from the client.
- **Route guards**: `app/(admin)/layout.jsx` and `app/(user)/layout.jsx` check the logged-in role and redirect anyone who doesn't belong there.
- **Auth is a bearer token**, not a cookie — `lib/api.js` attaches `Authorization: Bearer <token>` to every request after login/signup. The token and user object are both kept in `localStorage`.

## Ticket lifecycle

```
open  →  in_progress  →  resolved | closed
      (claim)          (resolve/close)
```

- Any employee can create a ticket (`category`, `office`, `comment` — all required).
- Any admin can **claim** an unclaimed ticket for themselves from the ticket detail modal — no picking a specific admin, it's self-service. This sets `assignedTo` to that admin and moves status to `in_progress`.
- Once claimed, any admin (not just the one who claimed it) can mark it **Resolved** or **Closed** from the same modal.
- Employees get a personal notification when their ticket is resolved or closed. Admins get broadcast notifications when a new ticket comes in or gets claimed.

All of this lives in the **ticket detail modal**, not on the row — click any ticket to open it. The row itself is just an informational preview (category, status, time).

## Comments

Every ticket has a comment thread (`GET`/`POST /api/comments/:ticket_id`), visible and postable by anyone who can see the ticket — both the employee who filed it and any admin. It's in the same detail modal, below the ticket info.

## What's NOT supported yet

- **File attachments** — there's no endpoint for this in the current API, so there's no upload/download UI. Removed intentionally rather than leaving a picker that silently does nothing.
- **Admin-to-admin assignment** — an earlier version of this API supported one admin assigning a ticket to a specific other admin. That's gone; the current model is self-claim only.

## Project structure

```
app/
  layout.jsx                    Root layout — wraps everything in AuthProvider
  login/page.jsx                 Shared login page (both roles)
  signup/page.jsx                 Signup — always creates an "employee" account
  (admin)/                         Admin route group — guarded, admin-only
    layout.jsx                     Redirects non-admins away
    page.jsx                       Dashboard        ("/") — tickets you've claimed
    tickets/page.jsx                 Every ticket, status tabs, claim/resolve/close via modal
    history/page.jsx                 Every ticket, read-only
    notifications/page.jsx            new_ticket + claimed broadcasts
    settings/page.jsx                  Create new admin accounts + view current admins
  (user)/                           Employee route group — guarded, employee-only
    layout.jsx                       Redirects non-employees away
    portal/page.jsx                   Dashboard        ("/portal")
    portal/tickets/page.jsx             Own tickets, status tabs
    portal/history/page.jsx              All of the employee's own tickets, read-only
    portal/settings/page.jsx              Read-only account info
    portal/notifications/page.jsx          Own resolved/closed updates only
components/
  Sidebar.jsx                       Nav — adapts links/labels by role, shows real user info, real logout
  TopBar.jsx                         Title + optional bell (configurable link per role) + optional CTA
  TicketRow.jsx                       One ticket row — category icon, status color, trailing time. Click to open detail modal
  TicketDetailModal.jsx                Full ticket info, comment thread, and (admins only) Claim / Resolve / Close actions
  NotificationItem.jsx                 Renders all 4 notification kinds: new_ticket / claimed / resolved / closed
  CreateTicketModal.jsx                 Create Ticket form — category + office + description, all required
  AuthShell.jsx                          Shared branded card wrapper for login/signup
lib/
  api.js                             The ONE place that knows the backend's base URL — every hook below calls apiFetch(). Also unwraps the backend's { detail: { error } } error shape.
  auth-context.jsx                  Client AuthProvider/useAuth
  useTickets.js                      Fetch/create tickets + claimTicket + updateTicketStatus
  useComments.js                      Fetch/post comments for a ticket
  useAdmins.js                        Fetch admins + createAdmin (Settings page only)
  useNotifications.js                  Fetch a specific person's notification feed
  formatDate.js                       Formats the backend's ISO 8601 datetimes for display
data/
  tickets.js                        Status → color/label map (open/in_progress/resolved/closed)
  categories.js                      Category → icon/label map (Email, Network, Hardware, Software, Other)
```

## Notes

- Role-based routing is enforced client-side (`user.role` from `AuthProvider`) — that's a UX guard, not a security boundary. The backend independently enforces admin-only actions (claim, resolve/close, create admin) regardless of what the client does, per the API docs.
- Category/comment/office values are sent exactly as entered — no client-side transformation.
- Brand accent is red throughout (CTAs, active nav, category icons), kept sparing everywhere else against a neutral black/white/gray base.
