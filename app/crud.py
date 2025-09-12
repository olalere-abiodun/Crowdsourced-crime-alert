from fastapi import HTTPException
from . import schemas, models
from sqlalchemy.orm import Session
from sqlalchemy import or_


# Create User CRUD 

def create_user(db: Session, user: schemas.UserCreate, hashed_password: str):
    db_user = models.Users(
        fullname=user.fullname,
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Check email and Username 
def check_user(db: Session, email: str = None, username: str = None, use_or: bool = False):
    query = db.query(models.Users)
    
    if email and username:
        if use_or:
            query = query.filter(or_(models.Users.email == email, models.Users.username == username))
        else:
            query = query.filter(models.Users.email == email, models.Users.username == username)
    elif email:
        query = query.filter(models.Users.email == email)
    elif username:
        query = query.filter(models.Users.username == username)
    
    return query.first()


#Create Crime
def create_crime(db: Session, user_id: int, crime: schemas.CrimeCreate):
    db_crime = models.Crimes(
        user_id=user_id,
        crime_type=crime.crime_type,
        description=crime.description,
        latitude=crime.latitude,
        longitude=crime.longitude,
        media_url=crime.media_url
    )
    db.add(db_crime)
    db.commit()
    db.refresh(db_crime)
    return db_crime

# Get crime by ID 
def get_crime_by_id(db: Session, crime_id: int):
    return db.query(models.Crimes).filter(models.Crimes.crime_id == crime_id).first()



    


