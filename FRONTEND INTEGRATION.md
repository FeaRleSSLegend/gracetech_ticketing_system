# GraceTech Ticketing API — Frontend Integration Guide

## Base URL

```
https://gracetech-ticketing-system.onrender.com
```

Free-tier Render instance, first request after inactivity can take 30–50s to respond while it spins back up. Not a bug, just a heads up so it doesn't look hung during a demo.

## Auth

Login and register both return a bearer token. Attach it to every request after that:

```
Authorization: Bearer <token>
```

There's no session/cookie, the API doesn't remember you between requests, the token is the only thing that does.

### `POST /api/auth/register`
```json
// request
{ "name": "string", "email": "string", "password": "string" }

// response
{
  "user": { "id": "string", "name": "string", "email": "string", "role": "employee" },
  "token": "string"
}
```
Every signup is created as `role: "employee"`, regardless of what's sent, there is no way to self-register as an admin. This is deliberate.

### `POST /api/auth/login`
```json
// request
{ "email": "string", "password": "string" }

// response — same shape as register
{ "user": { "id": "string", "name": "string", "email": "string", "role": "employee" | "admin" }, "token": "string" }
```

## Tickets

### `GET /api/tickets/`
Auth required (any role). Returns every ticket in the system.

### `POST /api/tickets/`
Auth required.
```json
// request
{
  "category": "email" | "network" | "hardware" | "software" | "other",
  "comment": "string",
  "office": "string"
}
```
`createdBy` is set server-side from the authenticated user, not from the body. `office` is free text (the department the ticket comes from), required, and not a fixed list.

### `POST /api/tickets/:id/claim`
**Admin only.** Takes **no request body** — an admin claims a ticket for themselves, so the claimer is read from the token.

Sets `assignedTo` to the claiming admin, `status` to `in_progress`, and `isNew` to `false`.

| Response | When |
| --- | --- |
| `200` | Claimed, returns the updated ticket |
| `409` | Already claimed by someone — `{ "detail": { "error": "This ticket has already been claimed" } }` |
| `404` | No ticket with that id |
| `401` | Caller isn't an admin |

### `PATCH /api/tickets/:id`
**Admin only.** Resolves or closes a ticket that is already being worked on.
```json
// request
{ "status": "resolved" | "closed" }
```
Only those two values are accepted — `"open"` and `"in_progress"` return `422`. A ticket must be claimed first; this is not a shortcut around claiming.

Sets `closedOn` to the current time (for both `resolved` and `closed`).

| Response | When |
| --- | --- |
| `200` | Updated, returns the ticket |
| `409` | Ticket isn't `in_progress` — `{ "detail": { "error": "Ticket must be in progress before it can be resolved or closed" } }` |
| `422` | Status was something other than `resolved` / `closed` |
| `404` | No ticket with that id |
| `401` | Caller isn't an admin |

### `DELETE /api/tickets/:id`
**Admin only.** Permanently deletes a ticket. No request body. There is no undo.

```json
// 200 response
{
  "detail": "Ticket deleted",
  "ticket": { "id": number, "comment": "string", "office": "string" },
  "deleted": { "notifications": number, "comments": number, "attachments": number }
}
```

The ticket's comments, attachments, and notifications go with it — `deleted` reports how many of each were removed. Any notification referencing this ticket disappears from `GET /notifications/` too, so refresh notification badges after a delete.

Works at any status: a ticket does not need to be resolved or closed first.

| Response | When |
| --- | --- |
| `200` | Deleted |
| `404` | No ticket with that id |
| `401` | Caller isn't an admin |

### Ticket shape (all ticket endpoints)
```json
{
  "id": number,
  "category": "email" | "network" | "hardware" | "software" | "other",
  "comment": "string",
  "office": "string",
  "status": "open" | "in_progress" | "resolved" | "closed",
  "createdBy": "string",
  "assignedTo": "string" | null,
  "isNew": boolean,
  "time": "ISO 8601 datetime",
  "closedOn": "ISO 8601 datetime" | null
}
```

## Comments

### `GET /api/comments/:ticket_id`
Auth required.

### `POST /api/comments/:ticket_id`
Auth required. `userId`/author is set server-side from the token, not the body.
```json
{ "body": "string" }
```

## Admins

### `GET /api/admins`
Auth required.

### `POST /api/admins`
**Admin only.** Creates a new admin account. `role` is forced to `"admin"` server-side.

### `DELETE /api/admins/:id`
**Admin only.** Removes another admin account. No request body.

```json
// 200 response
{
  "detail": "Admin removed",
  "admin": { "id": number, "name": "string", "email": "string" },
  "ticketsReleased": number
}
```

`ticketsReleased` is how many tickets that admin had claimed. Those tickets are handed back to the pool — `assignedTo` returns to `null` and an `in_progress` ticket goes back to `open`, so another admin can claim it. Refresh any ticket list after a successful delete, since rows you were showing as claimed may now be open.

| Response | When |
| --- | --- |
| `200` | Removed |
| `400` | You tried to remove your own account |
| `409` | Last remaining admin, or the admin filed tickets themselves (see below) |
| `404` | No admin with that id — also returned for an *employee's* id, since this route only sees admins |
| `401` | Caller isn't an admin |

Two refusals worth handling in the UI, both `409` with a readable `detail.error`:

- **"Cannot remove the last remaining admin"** — removing them would leave nobody able to reach any admin route.
- **"This admin filed N ticket(s) and cannot be removed."** — an admin who submitted tickets as a user. Their tickets would have to be destroyed along with the account, so the delete is refused instead. Delete those tickets first with `DELETE /api/tickets/:id`.

Their comments survive the delete with the author detached, and notifications they sent or received are removed.

## Users (employees)

Admin-facing management of employee accounts. Admins are managed separately under `/api/admins`.

### `GET /api/users`
**Admin only.** Every employee — admins are not included.

```json
{ "users": [ { "id": number, "name": "string", "email": "string" } ] }
```

Note the wrapper object, unlike `GET /api/admins` which returns a bare array.

### `DELETE /api/users/:id`
**Admin only.** Removes an employee account. No request body, and **`204` with an empty body on success** — don't try to parse JSON off it.

| Response | When |
| --- | --- |
| `204` | Deleted, no body |
| `409` | Employee has tickets — `{ "detail": { "error": "Cannot delete a user with existing tickets: ..." } }` |
| `403` | The id belongs to an admin — use `DELETE /api/admins/:id` instead |
| `404` | No user with that id |
| `401` | Caller isn't an admin |

**Most employees will hit the `409`**, since filing tickets is what employees do. To actually remove such an account, delete their tickets first with `DELETE /api/tickets/:id`. Their comments survive with the author detached; their notifications are removed.

## Notifications

### `GET /api/notifications/?name=<userName>`
Auth required. Returns broadcasts (`recipientName: null`) plus anything addressed to that **user** by name — employee or admin. Unknown name → empty list, not an error.

Pass the logged-in user's own `name` (from the login response). Employees get their own resolved/closed notifications this way; admins get the broadcasts plus anything aimed at them.

```json
{
  "notifications": [
    {
      "id": number,
      "kind": "new_ticket" | "claimed" | "resolved" | "closed",
      "recipientName": "string" | null,
      "actorName": "string",
      "ticketId": number,
      "category": "string",
      "comment": "string",
      "time": "ISO 8601 datetime"
    }
  ]
}
```
All four kinds fire automatically. The important distinction is **who they reach**:

| Kind | Fired by | Reaches |
| --- | --- | --- |
| `new_ticket` | `POST /tickets` | Broadcast — `recipientName: null`, every admin sees it |
| `claimed` | `POST /tickets/:id/claim` | Broadcast — so the rest of the admins see it's taken |
| `resolved` | `PATCH /tickets/:id` with `resolved` | **Targeted** — `recipientName` is the employee who filed it |
| `closed` | `PATCH /tickets/:id` with `closed` | **Targeted** — same |

`actorName` is always the person who caused it: the employee for `new_ticket`, the admin for the other three.

So an employee polling `?name=<their own name>` sees the broadcasts plus their own `resolved`/`closed` updates. If you want employees to see *only* their own updates, filter client-side on `recipientName !== null`.

## Breaking changes — assignment is now claiming

If you built against an earlier version of this doc, these three things changed:

1. **`POST /tickets/:id/assign` is gone.** Replaced by `POST /tickets/:id/claim`, which takes **no request body at all**. The old `{ "assigneeId": number }` payload no longer applies — one admin can no longer assign a ticket to a different admin, they can only claim it for themselves.
2. **`assignedBy` no longer exists** anywhere in the API. It's off the ticket shape, and there's no column behind it any more. `assignedTo` stays and now means "the admin who claimed this".
3. **Notification kind `"assigned"` is now `"claimed"`**, and it broadcasts rather than targeting one recipient.

Also new: **`office` is a required field** on `POST /tickets/` and appears on every ticket response. Omitting it returns `422`.

### Since then

4. **`PATCH /tickets/:id` is new** — the resolve/close step. Full ticket lifecycle is now: `POST /tickets` → `POST /tickets/:id/claim` → `PATCH /tickets/:id`.
5. **Notification `kind` gained `"resolved"` and `"closed"`.** If anything switches on `kind`, it needs branches for these or a sensible default — and unlike the first two, they're targeted rather than broadcast.
6. **`GET /notifications/?name=` is no longer admin-only.** It previously matched admins only, so passing an employee's name returned just the broadcasts. It now matches any user by name, which is what makes employee-targeted notifications reachable at all.
7. **`DELETE /admins/:id` is new** — admin removal. It can refuse with `409` in two cases, so don't assume success; surface `detail.error` to the user.
8. **`DELETE /tickets/:id` is new** — admin-only, permanent, and takes the ticket's comments and notifications with it. Worth a confirmation step in the UI.
9. **`GET /api/users` and `DELETE /api/users/:id` are new** — admin-facing employee management. The delete returns `204` with **no body**, unlike the admin and ticket deletes which return `200` with a JSON summary. Check the status code rather than assuming a body is there.

If you saw `GET /notifications/?name=` returning `500` (and what looked like a CORS error alongside it), that was one bug, not two: notification rows written before the `assigned` → `claimed` rename could not be loaded, and the crash meant no CORS headers were attached to the response. Fixed server-side; no frontend change needed.

## Two deliberate deviations from the original spec doc — please confirm these don't break anything on your end

1. **Roles are `employee` / `admin`**, not `user` / `admin`. If anything checks `role === "user"`, it needs to check `role === "employee"` instead.
2. **Status values are `open` / `in_progress` / `resolved` / `closed`** (4 states), not `open` / `pending` / `resolved`. Claiming a ticket moves it to `in_progress`, not `pending`.

## CORS

Currently allowed origins:

- `https://grace-tech-ticketing-system-fronten.vercel.app`
- `http://localhost:5500` and `http://127.0.0.1:5500`

If your dev server runs anywhere else (Vite's `:5173`, CRA's `:3000`), tell us the URL and we'll add it — an origin that isn't on this list fails in the browser even though the API itself is fine.

A CORS error in the console does not always mean a CORS misconfiguration. If the request also `500`s, the error handler returns before CORS headers are attached, so the browser reports it as a CORS failure. Check the response status before assuming it's an origin problem.