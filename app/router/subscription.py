from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app import schemas, crud, models
from app.dependencies import get_db
from app.router import auth_utils



router = APIRouter(prefix="/alerts", tags=["Alerts"])

# validation constants
MAX_RADIUS_KM = 100.0  
MIN_RADIUS_KM = 0.1


@router.post("/subscribe", response_model=schemas.SubscriptionResponse, status_code=status.HTTP_201_CREATED)
def subscribe_alert(
    subscription: schemas.SubscriptionCreate,
    db: Session = Depends(get_db),
    current_user: Optional[schemas.UserBase] = Depends(auth_utils.get_current_user)
):
    """
    Create or update an alerts subscription for the authenticated user.
    Body: { latitude, longitude, radius, is_active }
    """
    # require authentication
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required to create a subscription",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # basic validation
    lat = subscription.latitude
    lng = subscription.longitude
    radius = subscription.radius

    if not (-90.0 <= lat <= 90.0):
        raise HTTPException(status_code=400, detail="latitude must be between -90 and 90")
    if not (-180.0 <= lng <= 180.0):
        raise HTTPException(status_code=400, detail="longitude must be between -180 and 180")
    if radius is None or radius <= 0:
        raise HTTPException(status_code=400, detail="radius must be a positive number (in km)")
    if radius < MIN_RADIUS_KM or radius > MAX_RADIUS_KM:
        raise HTTPException(status_code=400, detail=f"radius must be between {MIN_RADIUS_KM} and {MAX_RADIUS_KM} km")

    # create or update subscription
    try:
        sub_obj = crud.upsert_subscription(db, current_user.user_id, subscription)
    except Exception as e:
        # log if you have a logger; return 500 for unexpected errors
        raise HTTPException(status_code=500, detail=str(e))

    return sub_obj


@router.get("/subscribe", response_model=schemas.SubscriptionResponse)
def get_subscription(
    db: Session = Depends(get_db),
    current_user: schemas.UserBase = Depends(auth_utils.get_current_user)
):
    """
    Get the current user's subscription details.
    """
    # require authentication
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required to view subscription"
        )

    sub_obj = crud.get_subscription_by_user(db, current_user.user_id)
    if not sub_obj:
        raise HTTPException(status_code=404, detail="No subscription found for the user")

    return sub_obj