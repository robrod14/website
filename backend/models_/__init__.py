from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Import all models so SQLAlchemy knows about them
from .registration import Registration, RegStatus
from .user import User
from .event import Event
from .admin_user import AdminUser  # ✅ make sure this is here
