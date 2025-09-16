from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app import schemas, crud, models
from app.dependencies import get_db
from app.router import auth_utils



router = APIRouter(prefix="/sos", tags=["SOS"])

@router.post("/send_sos", response_model=schemas.SOSResponse)
def send_sos_alert(
    sos_request: schemas.SOSCreate,
    db: Session = Depends(get_db),
    current_user: schemas.UserBase = Depends(auth_utils.get_current_user_optional)
):
    new_sos = crud.create_sos_alert(db, current_user.user_id, sos_request)
    return new_sos


@router.get("/sos_alerts", response_model=List[schemas.SOSResponse])
def get_all_sos_alerts(
    db: Session = Depends(get_db),
    current_user: schemas.UserBase = Depends(auth_utils.get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required to view all SOS alerts",
        )
    sos_alerts = crud.get_all_sos_alerts(db)
    return sos_alerts


