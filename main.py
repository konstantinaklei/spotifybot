
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, redirect, render_template, request
from dotenv import load_dotenv # <--- Πρόσθεσε αυτό

load_dotenv()

# 1. Ρυθμίσεις Spotify
# Διαβάζουμε τις τιμές από το περιβάλλον (Environment)
client_id = os.getenv('SPOTIPY_CLIENT_ID')
client_secret = os.getenv('SPOTIPY_CLIENT_SECRET')
redirect_uri = os.getenv('SPOTIPY_REDIRECT_URI')
scope = "user-top-read user-read-private user-read-email"

app = Flask(__name__)
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

@app.route('/')
def index():
    return '<h1>Spotify Bot</h1><a href="/login">Connect to Spotify</a>'

@app.route('/login')
def login():
    # Παίρνουμε το URL για το authentication από το Spotify
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    try:
        code = request.args.get('code')
        token_info = sp_oauth.get_access_token(code)
        sp = spotipy.Spotify(auth=token_info['access_token'])
        
        # Προσπάθησε να πάρεις τα στοιχεία
        user_info = sp.current_user()
        user_name = user_info['display_name']
        
        results = sp.current_user_top_tracks(limit=10, time_range='short_term')
        tracks = results['items']
        
    except Exception as e:
        # Αν υπάρξει σφάλμα (π.χ. 403), δώσε προκαθορισμένες τιμές
        print(f"Σφάλμα Spotify: {e}")
        user_name = "Χρήστης (Login Error)"
        tracks = [] 

    return render_template('index.html', user_name=user_name, tracks=tracks)
   
if __name__ == '__main__':
    # Τρέχουμε τον server στη θύρα 5000
    app.run(port=5000, debug=True)