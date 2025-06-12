import os, httpx, webbrowser, urllib.parse, time, json

AUTH_URL = os.getenv("ISSUER", "http://localhost:8000")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SEC = os.getenv("CLIENT_SECRET")
REDIRECT_URI = "http://localhost:3000/callback"
STATE = "xyz123"

# 1️⃣ Kick off login
params = urllib.parse.urlencode({
    "response_type": "code",
    "client_id": CLIENT_ID,
    "redirect_uri": REDIRECT_URI,
    "state": STATE,
})
webbrowser.open(f"{AUTH_URL}/oauth/authorize?{params}")

CODE = input("Paste ?code= from the redirect URL: ").strip()

async def exchange():
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{AUTH_URL}/oauth/token", data={
            "grant_type":"authorization_code",
            "code": CODE,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SEC,
        })
        r.raise_for_status()
        return r.json()

TOKENS = httpx.run(exchange())
print("Got tokens", json.dumps(TOKENS, indent=2))

ACCESS = TOKENS["access_token"]
REFRESH = TOKENS["refresh_token"]
EXP = time.time() + TOKENS["expires_in"]

async def call_protected():
    global ACCESS, REFRESH, EXP
    if time.time() > EXP - 60:
        async with httpx.AsyncClient() as client:
            r = await client.post(f"{AUTH_URL}/oauth/token", data={
                "grant_type": "refresh_token",
                "refresh_token": REFRESH,
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SEC,
            })
            r.raise_for_status()
            t = r.json()
            ACCESS, REFRESH, EXP = t["access_token"], t["refresh_token"], time.time()+t["expires_in"]
    # Use ACCESS in your API calls here
