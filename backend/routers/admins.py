from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.dependencies import get_current_user, get_db, require_role
from core.security import hash_password

from models.enums import RoleEnum
from models.user import User
from schemas.admin import AdminCreate, AdminRead

router = APIRouter(tags=["admins"])


@router.get("/", response_model=list[AdminRead])
def get_admins(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[User]:
    return db.query(User).filter(User.role == RoleEnum.admin).all()


@router.post("/", response_model=AdminRead)
def create_admin(
    admin_create: AdminCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(RoleEnum.admin)),
) -> User:
    existing_admin = db.query(User).filter(User.email == admin_create.email).first()
    if existing_admin is not None:
        raise HTTPException(status_code=400, detail="Email already registered")

    admin = User(
        name=admin_create.name,
        email=admin_create.email,
        password_hash=hash_password(admin_create.password),
        # Role is forced server-side; this endpoint only ever mints admins.
        role=RoleEnum.admin,
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin
