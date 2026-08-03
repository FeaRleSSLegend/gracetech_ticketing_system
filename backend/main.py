from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="GraceTech Helpdesk API",
    description="API for GraceTech Helpdesk application",
    version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter(prefix="/api/v1")

@router.get("/tickets/{ticket_id}")
def get_ticket():
    return "There are no ticket yet"