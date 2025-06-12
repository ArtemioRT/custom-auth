import os, secrets
from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from .database import get_db
from .models import User, OAuthClient, AuthCode
from .core.security import (
    hash_pw, verify_pw, new_access, new_refresh, decode, PUBLIC_KEY
)
from .seeder import seed

app = FastAPI(title="Custom OAuth2 / OIDC")
seed()  # create tables + demo data

LOGIN_HTML = """
<form method="post" action="/oauth/authorize">
 <input type="hidden" name="client_id" value="{cid}">
 <input type="hidden" name="redirect_uri" value="{ru}">
 <input type="hidden" name="state" value="{st}">
 <label>Email  <input name="email" type="email"     required></label><br>
 <label>Password<input name="password" type="password" required></label><br>
 <button>Sign in</button>
</form>
"""

@app.post("/auth/register", status_code=201)
def register(email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    if db.query(User).filter(User.email==email).first():
        raise HTTPException(400,"User exists")
    u = User(email=email, hashed_pw=hash_pw(password))
    db.add(u); db.commit(); db.refresh(u)
    return {"id":u.id,"email":u.email}

@app.get("/oauth/authorize")
def show_login(client_id:str, redirect_uri:str, state:str, db:Session=Depends(get_db)):
    c = db.get(OAuthClient, client_id)
    if not c or c.redirect_uri!=redirect_uri:
        raise HTTPException(400,"Invalid client")
    return HTMLResponse(LOGIN_HTML.format(cid=client_id, ru=redirect_uri, st=state))

@app.post("/oauth/authorize")
def do_login(
    email:str=Form(...), password:str=Form(...),
    client_id:str=Form(...), redirect_uri:str=Form(...), state:str=Form(...),
    db:Session=Depends(get_db)
):
    user = db.query(User).filter(User.email==email).first()
    if not user or not verify_pw(password, user.hashed_pw):
        raise HTTPException(401,"Bad credentials")
    code = secrets.token_urlsafe(32)
    db.add(AuthCode(code=code, user_id=user.id, client_id=client_id,
                    expires_at=datetime.utcnow()+timedelta(minutes=10)))
    db.commit()
    return RedirectResponse(f"{redirect_uri}?code={code}&state={state}", status_code=302)

@app.post("/oauth/token")
def token(
    grant_type:str=Form(...),
    code:str=None, refresh_token:str=None,
    client_id:str=Form(...), client_secret:str=Form(...),
    db:Session=Depends(get_db)
):
    cli = db.get(OAuthClient, client_id)
    if not cli or cli.secret!=client_secret:
        raise HTTPException(401,"Bad client credentials")

    if grant_type=="authorization_code":
        ac = db.get(AuthCode, code)
        if not ac or ac.expires_at<datetime.utcnow():
            raise HTTPException(400,"Invalid code")
        uid = ac.user_id
        db.delete(ac); db.commit()
    elif grant_type=="refresh_token":
        try:
            payload = decode(refresh_token)
            if payload["scope"]!="refresh": raise ValueError
            uid = int(payload["sub"])
        except Exception:
            raise HTTPException(400,"Bad refresh token")
    else:
        raise HTTPException(400,"Unsupported grant")

    access  = new_access(uid)
    refresh = new_refresh(uid)
    return {
      "access_token": access,
      "refresh_token": refresh,
      "token_type": "bearer",
      "expires_in": int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))*60
    }

@app.get("/.well-known/jwks.json")
def jwks():
    from jose import jwk
    k = jwk.construct(PUBLIC_KEY, "RS256")
    return {"keys":[k.to_dict()]}

@app.get("/.well-known/openid-configuration")
def discovery():
    base = os.getenv("ISSUER")
    return {
        "issuer": base,
        "authorization_endpoint": f"{base}/oauth/authorize",
        "token_endpoint": f"{base}/oauth/token",
        "jwks_uri": f"{base}/.well-known/jwks.json",
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code","refresh_token"],
    }
