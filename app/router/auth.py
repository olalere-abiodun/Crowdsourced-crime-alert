from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app import schemas, crud, models
from app.dependencies import get_db
from app.router import auth_utils


router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/signup")
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if email or username already exists
    if crud.check_user(db, email=user.email, username=user.username, use_or=True):
        raise HTTPException(status_code=400, detail="Email or username already taken")
    hashed_password = auth_utils.pwd_context.hash(user.password)
    new_user = crud.create_user(db, user, hashed_password)
    return {"message": "User created successfully", "username": new_user.username}


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = auth_utils.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = auth_utils.create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=auth_utils.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me/", response_model=schemas.UserResponse)
async def get_me(current_user: schemas.UserBase = Depends(auth_utils.get_current_user)):
    return current_user


@router.put("/users/me", response_model=schemas.UserResponse)
async def update_user_profile(
    updateUser: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.Users = Depends(auth_utils.get_current_user)
):
    user = current_user

    if updateUser.fullname:
        user.fullname = updateUser.fullname
    if updateUser.username:
        user.username = updateUser.username

    # ✅ Update password securely
    if updateUser.old_password and updateUser.new_password:
        if not auth_utils.pwd_context.verify(updateUser.old_password, user.hashed_password):
            raise HTTPException(status_code=400, detail="Old password is incorrect")

        user.hashed_password = auth_utils.pwd_context.hash(updateUser.new_password)

    db.commit()
    db.refresh(user)

    return user