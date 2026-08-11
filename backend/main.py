from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import init_db
from routers import admins, auth, comments, notifications, tickets


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(title="Enterprise IT Support Ticketing System", lifespan=lifespan)

init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500", "http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(tickets.router, prefix="/api/tickets", tags=["tickets"])
app.include_router(admins.router, prefix="/api/admins", tags=["admins"])
app.include_router(comments.router, prefix="/api/comments", tags=["comments"])
app.include_router(
    notifications.router, prefix="/api/notifications", tags=["notifications"]
)
