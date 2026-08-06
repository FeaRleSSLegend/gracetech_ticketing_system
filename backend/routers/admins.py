from ..schemas.admin import AdminCreate, AdminRead
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.dependencies import get_db
from models.user import User
from core.security import hash_password


router = APIRouter()

@router.get("/admins", response_model=AdminRead)
def get_admins(db: Session = Depends(get_db)) -> AdminRead:
    admins = db.query(User).filter(User.role == "admin").all()
    return [AdminRead.model_validate(admin) for admin in admins]

@router.post("/admins", response_model=AdminRead)
def create_admin(admin_create: AdminCreate, db: Session = Depends(get_db)) -> AdminRead:
    existing_admin = db.query(User).filter(User.email == admin_create.email).first()
    if existing_admin is not None:
        raise HTTPException(status_code=400, detail="Email already registered")

    admin = User(
        name=admin_create.name,
        email=admin_create.email,
        password_hash=hash_password(admin_create.password),
        role=admin_create.role,
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return AdminRead.model_validate(admin)