from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.dependencies import get_db
from core.security import create_access_token, hash_password, verify_password
from models.user import User
from schemas.user import TokenResponse, UserCreate, UserLogin, UserRead

router = APIRouter(tags=["auth"])


@router.post("/register", response_model=UserRead)
def register(user_create: UserCreate, db: Session = Depends(get_db)) -> User:
    existing_user = db.query(User).filter(User.email == user_create.email).first()
    if existing_user is not None:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        name=user_create.name,
        email=user_create.email,
        password_hash=hash_password(user_create.password),
        role=user_create.role,
        created_at=date.today(),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
def login(credentials: UserLogin, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.query(User).filter(User.email == credentials.email).first()
    if user is None or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = create_access_token({"sub": str(user.id)})
    return TokenResponse(token=token, user=UserRead.model_validate(user))
