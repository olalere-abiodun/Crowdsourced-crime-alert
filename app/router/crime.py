from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app import schemas, crud, models
from app.dependencies import get_db
from app.router import auth_utils
import math

router = APIRouter(prefix="/crime", tags=["Crime"])

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.asin(math.sqrt(a))
    return R * c


@router.post("/crimes")
def create_crime(
    crime: schemas.CrimeCreate, 
    db: Session = Depends(get_db),
    current_user: schemas.UserBase = Depends(auth_utils.get_current_user)):
        
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try: 
        new_crime = crud.create_crime(db, current_user.user_id, crime)
        return {"message": "Crime created successfully", "crime": [new_crime]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# get all crime and filter by long anf lat

@router.get("/", response_model=List[schemas.CrimeResponse])
def get_crimes(
    crime_type: Optional[str] = Query(None, description="Filter by crime type"),
    radius: Optional[float] = Query(None, description="Radius in km"),
    lat: Optional[float] = Query(None, description="Latitude for radius filter"),
    lng: Optional[float] = Query(None, description="Longitude for radius filter"),
    db: Session = Depends(get_db),
):
    query = db.query(models.Crimes)

    # ✅ Filter by crime type
    if crime_type:
        query = query.filter(models.Crimes.crime_type.ilike(f"%{crime_type}%"))

    crimes = query.all()

    # ✅ Apply radius filter in Python
    if radius and lat and lng:
        crimes = [
            c for c in crimes
            if haversine(lat, lng, c.latitude, c.longitude) <= radius
        ]

    return crimes

@router.get("/{crime_id}", response_model=schemas.CrimeResponse)
def get_crime(crime_id: int, db: Session = Depends(get_db)):
    crime = crud.get_crime_by_id(db, crime_id)
    if not crime:
        raise HTTPException(status_code=404, detail="Crime not found")
    return crime

@router.put("/{crime_id}", response_model=schemas.CrimeResponse)
def update_crime(crime_id: int, crime: schemas.CrimeUpdate, db: Session = Depends(get_db), current_user: schemas.UserBase = Depends(auth_utils.get_current_user)):
    db_crime = crud.get_crime_by_id(db, crime_id)

    if not db_crime:
        raise HTTPException(status_code=404, detail="Crime not found")

    if db_crime.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this crime")
    
    update_data = crime.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_crime, key, value)


    db.commit()
    db.refresh(db_crime)

    return db_crime


@router.delete("/{crime_id}")
def delete_crime(crime_id: int, db: Session = Depends(get_db), current_user: schemas.UserBase = Depends(auth_utils.get_current_user)):
    db_crime = crud.get_crime_by_id(db, crime_id)

    if db_crime.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this crime")

    db.delete(db_crime)
    db.commit()

    return {"message": "Crime deleted successfully"}


    



