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

# create a vote
from fastapi import HTTPException, status

def create_vote(db: Session, crime_id: int, user_id: int, vote: schemas.VoteRequest):
    # Check if user already voted for this crime
    existing_vote = db.query(models.Votes).filter_by(
        crime_id=crime_id, user_id=user_id
    ).first()

    if existing_vote:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already voted on this crime"
        )

    new_vote = models.Votes(
        crime_id=crime_id,
        user_id=user_id,
        vote_type=vote.vote_type
    )
    db.add(new_vote)
    db.commit()
    db.refresh(new_vote)
    return new_vote


from fastapi import HTTPException, status

def create_anonymous_vote(db: Session, crime_id: int, vote: schemas.VoteRequest, ip_address: str):
    # Check if this IP already voted on this crime
    existing_vote = db.query(models.AnonymousVotes).filter_by(
        crime_id=crime_id, ip_address=ip_address
    ).first()

    if existing_vote:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already voted on this crime anonymously"
        )

    new_vote = models.AnonymousVotes(
        crime_id=crime_id,
        ip_address=ip_address,
        vote_type=vote.vote_type
    )
    db.add(new_vote)
    db.commit()
    db.refresh(new_vote)
    return new_vote


def get_subscription_by_user(db: Session, user_id: int):
    return db.query(models.Subscription).filter(models.Subscription.user_id == user_id).first()

def create_subscription(db: Session, user_id: int, sub: schemas.SubscriptionCreate):
    db_sub = models.Subscription(
        user_id=user_id,
        latitude=sub.latitude,
        longitude=sub.longitude,
        radius=sub.radius,
        is_active=sub.is_active if sub.is_active is not None else True,
        created_at=datetime.utcnow()
    )
    db.add(db_sub)
    db.commit()
    db.refresh(db_sub)
    return db_sub

def update_subscription(db: Session, db_sub: models.Subscription, sub: schemas.SubscriptionCreate):
    db_sub.latitude = sub.latitude
    db_sub.longitude = sub.longitude
    db_sub.radius = sub.radius
    db_sub.is_active = sub.is_active if sub.is_active is not None else db_sub.is_active
    db.commit()
    db.refresh(db_sub)
    return db_sub

def upsert_subscription(db: Session, user_id: int, sub: schemas.SubscriptionCreate):
    existing = get_subscription_by_user(db, user_id)
    if existing:
        return update_subscription(db, existing, sub)
    return create_subscription(db, user_id, sub)
    


