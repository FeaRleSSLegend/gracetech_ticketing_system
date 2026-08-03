from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import models  # noqa: F401  (registers all mapped classes before create_all)
from database import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Enterprise IT Support Ticketing System", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500", "http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers are added here once routers/ are implemented:
# from routers import auth, tickets, comments, attachments
# app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
# app.include_router(tickets.router, prefix="/api/tickets", tags=["tickets"])
# app.include_router(comments.router, tags=["comments"])
# app.include_router(attachments.router, tags=["attachments"])