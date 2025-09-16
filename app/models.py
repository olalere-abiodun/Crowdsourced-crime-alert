from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, UTC
from .database import Base


class Users(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True, unique=True)
    fullname = Column(String, nullable=False)
    username = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    role = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))

    crimes = relationship("Crimes", back_populates="user")
    votes = relationship("Votes", back_populates="user")
    subscriptions = relationship("Subscription", back_populates="user")
    sos_alerts = relationship("SOSAlerts", back_populates="user", cascade="all, delete-orphan")
    flagged_crimes = relationship("FlaggedCrime", back_populates="admin")


class Crimes(Base):
    __tablename__ = "crimes"

    crime_id = Column(Integer, primary_key=True, index=True, unique=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    crime_type = Column(String, nullable=False)
    description = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    media_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    user = relationship("Users", back_populates="crimes")
    votes = relationship("Votes", back_populates="crime", cascade="all, delete-orphan")
    anonymous_votes = relationship("AnonymousVotes", back_populates="crime", cascade="all, delete-orphan")
    flags = relationship("FlaggedCrime", back_populates="crime", cascade="all, delete-orphan")


class Votes(Base):
    __tablename__ = "votes"

    vote_id = Column(Integer, primary_key=True, index=True, unique=True, autoincrement=True)
    crime_id = Column(Integer, ForeignKey("crimes.crime_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    vote_type = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))

    __table_args__ = (
        UniqueConstraint("crime_id", "user_id", name="unique_user_vote"),
    )

    user = relationship("Users", back_populates="votes")
    crime = relationship("Crimes", back_populates="votes")


class AnonymousVotes(Base):
    __tablename__ = "anonymous_votes"

    vote_id = Column(Integer, primary_key=True, autoincrement=True)
    crime_id = Column(Integer, ForeignKey("crimes.crime_id", ondelete="CASCADE"), nullable=False)
    ip_address = Column(String, nullable=False)
    vote_type = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    

    __table_args__ = (
        UniqueConstraint("crime_id", "ip_address", name="unique_anon_vote"),
    )

    crime = relationship("Crimes", back_populates="anonymous_votes")


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True, unique=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    radius = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))

    user = relationship("Users", back_populates="subscriptions")

class FlaggedCrime(Base):
    __tablename__ = "flagged_crimes"

    id = Column(Integer, primary_key=True, index=True)
    crime_id = Column(Integer, ForeignKey("crimes.crime_id"), nullable=False)
    flagged_by = Column(Integer, ForeignKey("users.user_id"))
    reason = Column(String, default="No reason provided")
    is_flagged = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))

    # relationships
    crime = relationship("Crimes", back_populates="flags")
    admin = relationship("Users", back_populates="flagged_crimes") 


class SOSAlerts(Base):
    __tablename__ = "sos_alerts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=True)  # Nullable for anonymous alerts
    message = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))

    user = relationship("Users", back_populates="sos_alerts")