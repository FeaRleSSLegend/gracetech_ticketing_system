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
{ "category": "email" | "network" | "hardware" | "software" | "other", "comment": "string" }
```
`createdBy` is set server-side from the authenticated user, not from the body.

### `POST /api/tickets/:id/assign`
**Admin only.**
```json
// request
{ "assigneeId": number }
```
`assignedBy` and the status transition are derived server-side from the authenticated user, not from the body.

### Ticket shape (all ticket endpoints)
```json
{
  "id": number,
  "category": "email" | "network" | "hardware" | "software" | "other",
  "comment": "string",
  "status": "open" | "in_progress" | "resolved" | "closed",
  "createdBy": "string",
  "assignedTo": "string" | null,
  "assignedBy": "string" | null,
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

### `GET /api/notifications/?name=<adminName>`
Auth required. Returns broadcasts (`recipientName: null`) plus anything addressed to that admin by name. Unknown name → empty list, not an error.

```json
{
  "notifications": [
    {
      "id": number,
      "kind": "new_ticket" | "assigned",
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
Fires automatically: `new_ticket` (broadcast) on every `POST /tickets`, `assigned` (targeted at the assignee) on every successful `POST /tickets/:id/assign`.

## Three deliberate deviations from the original spec doc — please confirm these don't break anything on your end

1. **Roles are `employee` / `admin`**, not `user` / `admin`. If anything checks `role === "user"`, it needs to check `role === "employee"` instead.
2. **Status values are `open` / `in_progress` / `resolved` / `closed`** (4 states), not `open` / `pending` / `resolved`. Assigning a ticket moves it to `in_progress`, not `pending`.
3. **Assignment is by ID, not name.** `POST /tickets/:id/assign` takes `assigneeId`, not `assigneeName`. Use `GET /api/admins` to get real IDs to assign against.

## CORS

Dev origin (`http://localhost:3000` or whatever your dev server runs on) needs to be confirmed as allowed on the backend, let us know your actual dev URL if it's not the default.