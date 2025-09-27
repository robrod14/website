from sqlalchemy import Column, String, Integer, DateTime, Enum, ForeignKey, Boolean
from sqlalchemy.dialects.sqlite import BLOB
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import enum

Base = declarative_base()

class AdminUser(Base):
    __tablename__ = "admin_users"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    is_superadmin = Column(Boolean, default=False)

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

class RegStatus(enum.Enum):
    pending_payment = "pending_payment"
    registered = "registered"
    waitlist = "waitlist"
    cancelled = "cancelled"

class Event(Base):
    __tablename__ = "events"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    location = Column(String)
    date = Column(String)     # store as string for simplicity
    time = Column(String)     # store as string for simplicity
    courts = Column(String)
    capacity = Column(Integer, default=9)
    price_cents = Column(Integer, default=0)
    is_signups_open = Column(Boolean, default=False)
    organizer_phone = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    phone_encrypted = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Registration(Base):
    __tablename__ = "registrations"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    event_id = Column(String, ForeignKey("events.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    status = Column(Enum(RegStatus), default=RegStatus.pending_payment)
    payment_memo = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    paid_at = Column(DateTime(timezone=True), nullable=True)
