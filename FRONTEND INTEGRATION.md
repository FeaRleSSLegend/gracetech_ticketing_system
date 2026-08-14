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

## Two deliberate deviations from the original spec doc — please confirm these don't break anything on your end

1. **Roles are `employee` / `admin`**, not `user` / `admin`. If anything checks `role === "user"`, it needs to check `role === "employee"` instead.
2. **Status values are `open` / `in_progress` / `resolved` / `closed`** (4 states), not `open` / `pending` / `resolved`. Claiming a ticket moves it to `in_progress`, not `pending`.

## CORS

Dev origin (`http://localhost:3000` or whatever your dev server runs on) needs to be confirmed as allowed on the backend, let us know your actual dev URL if it's not the default.