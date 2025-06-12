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
            redirect_uri="https://custom-auth-dum1.onrender.com/callback",
            secret=secrets.token_urlsafe(32)
        )
        db.add(client)
        db.commit()
        print("🔑  Demo client_id:", client.id)
        print("🔑  Demo client_secret:", client.secret)
    
    # Bot Framework client - CON EL CLIENT_ID ESPECÍFICO QUE NECESITAS
    bot_client_id = "62eeaf14-c15f-4eae-a073-0e289b21e934"
    if not db.query(OAuthClient).filter_by(id=bot_client_id).first():
        bot_client = OAuthClient(
            id=bot_client_id,  # ID específico que Bot Framework espera
            name="BotFrameworkClient",
            redirect_uri="https://token.botframework.com/.auth/web/redirect",
            secret=secrets.token_urlsafe(32)
        )
        db.add(bot_client)
        db.commit()
        print("🤖  Bot Framework client_id:", bot_client.id)
        print("🤖  Bot Framework client_secret:", bot_client.secret)
    
    db.close()