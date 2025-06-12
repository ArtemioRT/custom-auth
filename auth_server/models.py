from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_pw = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class OAuthClient(Base):
    __tablename__ = "oauth_clients"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    redirect_uri = Column(String, nullable=False)
    secret = Column(String, nullable=False)

class AuthCode(Base):
    __tablename__ = "auth_codes"
    code = Column(String, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    client_id = Column(String, ForeignKey("oauth_clients.id"))
    expires_at = Column(DateTime)
    user = relationship("User")
