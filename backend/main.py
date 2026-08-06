from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import init_db
from routers.auth import router as auth_router
from routers import auth, tickets, comments, attachments




app = FastAPI(title="Ticketing System API")
app.include_router(auth_router)
init_db()


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(title="Enterprise IT Support Ticketing System", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500", "http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(tickets.router, prefix="/api/tickets", tags=["tickets"])
# app.include_router(comments.router, prefix="/api/comments", tags=["comments"])
# app.include_router(attachments.router, prefix="/api/attachments", tags=["attachments"])


