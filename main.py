
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv  # <--- Πρόσθεσε αυτό

load_dotenv()

# 1. Ρυθμίσεις Spotify
# Διαβάζουμε τις τιμές από το περιβάλλον (Environment)
client_id = os.getenv('SPOTIPY_CLIENT_ID')
client_secret = os.getenv('SPOTIPY_CLIENT_SECRET')
redirect_uri = os.getenv('SPOTIPY_REDIRECT_URI')
scope = "user-top-read user-read-private user-read-email"

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Πριν το sp_oauth, αν υπάρχει παλιά cache, σβήσε την
if os.path.exists(".cache_temp"):
    os.remove(".cache_temp")
# Δημιουργία του αντικειμένου OAuth για να το χρησιμοποιούμε παντού
sp_oauth = SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope=scope,
    show_dialog=True,
    cache_path=".cache_temp" # Δίνουμε ένα όνομα αρχείου
)

@app.get('/', response_class=HTMLResponse)
async def index():
    return '<h1>Spotify Bot</h1><a href="/login">Connect to Spotify</a>'

@app.get('/login')
async def login():
    # Παίρνουμε το URL για το authentication από το Spotify
    auth_url = sp_oauth.get_authorize_url()
    return RedirectResponse(url=auth_url)

@app.get('/callback', response_class=HTMLResponse)
async def callback(request: Request):
    try:
        code = request.query_params.get('code')
        print(f"=== CALLBACK DEBUG ===")
        print(f"Code received: {code[:20]}..." if code else "No code received!")
        
        token_info = sp_oauth.get_access_token(code)
        print(f"Token received successfully!")
        print(f"Token scopes: {token_info.get('scope', 'N/A')}")
        
        sp = spotipy.Spotify(auth=token_info['access_token'])
        
        # Προσπάθησε να πάρεις τα στοιχεία
        print("Calling sp.current_user()...")
        user_info = sp.current_user()
        user_name = user_info['display_name']
        print(f"User: {user_name}")
        
        print("Calling sp.current_user_top_tracks()...")
        results = sp.current_user_top_tracks(limit=10, time_range='short_term')
        tracks = results['items']
        print(f"Got {len(tracks)} tracks")
        
    except spotipy.exceptions.SpotifyException as e:
        print(f"=== SPOTIFY API ERROR ===")
        print(f"HTTP Status: {e.http_status}")
        print(f"Code: {e.code}")
        print(f"Message: {e.msg}")
        print(f"Reason: {e.reason}")
        print(f"Headers: {e.headers}")
        user_name = "Χρήστης (Login Error)"
        tracks = []
    except Exception as e:
        print(f"=== GENERAL ERROR ===")
        print(f"Type: {type(e).__name__}")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        user_name = "Χρήστης (Login Error)"
        tracks = [] 

    return templates.TemplateResponse("index.html", {"request": request, "user_name": user_name, "tracks": tracks})
   
if __name__ == '__main__':
    import uvicorn
    # Τρέχουμε τον server στη θύρα 5000
    uvicorn.run(app, host="127.0.0.1", port=5000)