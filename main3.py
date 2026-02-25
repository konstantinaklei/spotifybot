import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

load_dotenv()

# Ρυθμίσεις από το .env
client_id = os.getenv('SPOTIPY_CLIENT_ID')
client_secret = os.getenv('SPOTIPY_CLIENT_SECRET')
redirect_uri = os.getenv('SPOTIPY_REDIRECT_URI')
scope = "user-top-read user-read-private user-read-email"

app = FastAPI()

# Βεβαιώσου ότι οι φάκελοι static και templates υπάρχουν
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

def get_spotify_oauth():
    return SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope=scope,
        show_dialog=True,
        cache_path=None 
    )

@app.get('/', response_class=HTMLResponse)
async def index():
    return '<h1>Spotify Bot</h1><a href="/login">Σύνδεση στο Spotify</a>'

@app.get('/login')
async def login():
    sp_oauth = get_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return RedirectResponse(url=auth_url)

@app.get('/callback', response_class=HTMLResponse)
async def callback(request: Request):
    sp_oauth = get_spotify_oauth()
    code = request.query_params.get('code')
    
    if not code:
        return HTMLResponse("Σφάλμα: Δεν λάβαμε κωδικό από το Spotify.")

    try:
        # ΔΙΟΡΘΩΣΗ: Παίρνουμε το dictionary με το token
        token_info = sp_oauth.get_access_token(code, as_dict=True)
        
        # ΠΡΟΣΟΧΗ: Χρειαζόμαστε ΜΟΝΟ το string του access_token
        access_token = token_info['access_token']
        
        # Δημιουργία Spotify Client
        sp = spotipy.Spotify(auth=access_token)
        
        # Λήψη στοιχείων χρήστη
        user_info = sp.current_user()
        user_name = user_info.get('display_name', 'User')
        
        # Λήψη Top 10 Tracks
        results = sp.current_user_top_tracks(limit=10, time_range='short_term')
        tracks = results.get('items', [])
        
        return templates.TemplateResponse("index.html", {
            "request": request, 
            "user_name": user_name, 
            "tracks": tracks
        })

    except Exception as e:
        print(f"Σφάλμα κατά τη σύνδεση: {e}")
        return HTMLResponse(f"<h1>Πρόβλημα Σύνδεσης</h1><p>{e}</p><a href='/login'>Δοκίμασε ξανά</a>")

if __name__ == '__main__':
    import uvicorn
    # Τρέχει στην πόρτα 5000
    uvicorn.run(app, host="127.0.0.1", port=5000)