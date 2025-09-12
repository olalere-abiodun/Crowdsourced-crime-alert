from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from typing import List, Optional
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import func
from sqlalchemy.orm import Session
from app import schemas, crud, models
from app.dependencies import get_db
from app.router import auth_utils


router = APIRouter(prefix="/vote", tags=["Vote"])


@router.post("/crimes/{crime_id}/vote", response_model=schemas.VoteResponse)
def create_vote(
    crime_id: int,
    vote: schemas.VoteRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[schemas.UserBase] = Depends(auth_utils.get_current_user_optional),
):
    if current_user:
        return crud.create_vote(db, crime_id, current_user.user_id, vote)
    else:
        ip_address = request.client.host
        return crud.create_anonymous_vote(db, crime_id, vote, ip_address)






@router.get("/crimes/{crime_id}/votes")
def get_votes(
    crime_id: int,
    db: Session = Depends(get_db),
):
    # Get authenticated votes count
    auth_votes = db.query(models.Votes.vote_type, func.count(models.Votes.vote_id)) \
        .filter(models.Votes.crime_id == crime_id) \
        .group_by(models.Votes.vote_type) \
        .all()

    # Get anonymous votes count
    anon_votes = db.query(models.AnonymousVotes.vote_type, func.count(models.AnonymousVotes.vote_id)) \
        .filter(models.AnonymousVotes.crime_id == crime_id) \
        .group_by(models.AnonymousVotes.vote_type) \
        .all()

    # Convert results into dictionaries
    result = {
        "authenticated": {vote_type: count for vote_type, count in auth_votes},
        "anonymous": {vote_type: count for vote_type, count in anon_votes},
    }

    # Optionally add a total aggregation
    total_votes = {}
    for section in ["authenticated", "anonymous"]:
        for vote_type, count in result[section].items():
            total_votes[vote_type] = total_votes.get(vote_type, 0) + count

    result["total"] = total_votes

    return result

                
    