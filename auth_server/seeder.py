import os, secrets
from .models import Base, User, OAuthClient
from .core.security import hash_pw
from .database import engine, SessionLocal

def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    # Demo user
    if not db.query(User).filter_by(email=os.getenv("SEED_EMAIL")).first():
        user = User(
            email=os.getenv("SEED_EMAIL"),
            hashed_pw=hash_pw(os.getenv("SEED_PASSWORD"))
        )
        db.add(user)
        db.commit()
    # Demo OAuth client
    if not db.query(OAuthClient).filter_by(name="DemoClient").first():
        client = OAuthClient(
            name="DemoClient",
            redirect_uri="http://localhost:3000/callback",
            secret=secrets.token_urlsafe(32)
        )
        db.add(client)
        db.commit()
        print("🔑  Demo client_id:", client.id)
        print("🔑  Demo client_secret:", client.secret)
    db.close()
