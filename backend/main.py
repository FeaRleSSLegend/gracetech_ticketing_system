from fastapi import FastAPI

from database import init_db
from routers.auth import router as auth_router

app = FastAPI(title="Ticketing System API")
app.include_router(auth_router)
init_db()


@app.get("/")
def read_root():
    return {"message": "Ticketing API is running"}
