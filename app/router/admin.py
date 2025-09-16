from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app import schemas, crud, models
from app.dependencies import get_db
from app.router import auth_utils
from sqlalchemy import func


router = APIRouter(prefix="/admin", tags=["Admin"])

@router.post("/crime/{crime_id}/flag", response_model=schemas.FlaggedCrimeOut)
def flag_crime(
    crime_id: int,
    flag: schemas.FlaggedCrimeCreate,
    db: Session = Depends(get_db),
    current_user: schemas.UserBase = Depends(auth_utils.get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")

    crime = crud.get_crime_by_id(db, crime_id)
    if not crime:
        raise HTTPException(status_code=404, detail="Crime not found")

    flagged = crud.create_flagged_crime(
        db,
        crime_id=crime.crime_id,
        flagged_by=current_user.user_id,
        reason=flag.reason,
        is_flagged=flag.is_flagged
    )
    db.commit()
    db.refresh(flagged)

    return flagged

@router.get("/crimes/flagged", response_model=List[schemas.FlaggedCrimeOut])
def get_flagged_crimes(
    db: Session = Depends(get_db),
    current_user: schemas.UserBase = Depends(auth_utils.get_current_user),
):
    # if current_user.role != "admin":
    #     raise HTTPException(status_code=403, detail="Admins only")

    flagged_crimes = crud.get_flagged_crimes(db)
    return flagged_crimes



# to start today 

@router.get("/statistics")
def get_statistics(
    db: Session = Depends(get_db),
    current_user: schemas.UserBase = Depends(auth_utils.get_current_user)
):
    
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")

    # total reports
    total_reports = db.query(func.count(models.Crimes.crime_id)).scalar()

    # top crime types
    top_types = (
        db.query(models.Crimes.crime_type, func.count(models.Crimes.crime_id))
        .group_by(models.Crimes.crime_type)
        .order_by(func.count(models.Crimes.crime_id).desc())
        .limit(5)
        .all()
    )

    # hotspots (group by lat/long)
    hotspots = (
        db.query(
            models.Crimes.latitude,
            models.Crimes.longitude,
            func.count(models.Crimes.crime_id).label("crime_count")
        )
        .group_by(models.Crimes.latitude, models.Crimes.longitude)
        .order_by(func.count(models.Crimes.crime_id).desc())
        .limit(5)
        .all()
    )

    return {
        "total_reports": total_reports,
        "top_crime_types": [{"type": t[0], "count": t[1]} for t in top_types],
        "hotspots": [
            {
                "location": {"latitude": h.latitude, "longitude": h.longitude},
                "crime_count": h.crime_count,
            }
            for h in hotspots
        ],
    }



