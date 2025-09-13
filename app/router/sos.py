from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app import schemas, crud, models
from app.dependencies import get_db
from app.router import auth_utils



router = APIRouter(prefix="/sos", tags=["SOS"])

@router.post("/send", status_code=status.HTTP_200_OK)
def send_sos_alert(
    sos_request: schemas.SOSRequest,
    db: Session = Depends(get_db),
    current_user: Optional[schemas.UserBase] = Depends(auth_utils.get_current_user_optional)
):
    """
    Endpoint to send an SOS alert.
    Body: { latitude, longitude, message (optional) }
    """
    # If user is authenticated, use their user_id; otherwise, use None for anonymous
    user_id = current_user.user_id if current_user else None

    try:
        # Create SOS alert in the database
        sos_alert = crud.create_sos_alert(db, user_id, sos_request)
        return {"message": "SOS alert sent successfully", "sos_alert": sos_alert}
    except Exception as e:
        # Log the error if you have a logger; return 500 for unexpected errors
        raise HTTPException(status_code=500, detail=str(e))