from flask import Flask, render_template, request
import requests
import os
from datetime import datetime, timedelta

app = Flask(__name__)

# Configuration de l'API
CLIENT_ID = "4lw8awe386w7lhqc7p9qt34nm14sj1"
CLIENT_SECRET = "a3l1uk0p024bjyew6kdytt6hwn87d0"
BASE_URL = "https://api.twitch.tv/helix/"

def get_access_token():
    url = "https://id.twitch.tv/oauth2/token"
    params = {"client_id": CLIENT_ID, "client_secret": CLIENT_SECRET, "grant_type": "client_credentials"}
    response = requests.post(url, params=params)
    response.raise_for_status()
    return response.json()["access_token"]

def get_streamer_id(username, access_token):
    headers = {"Client-ID": CLIENT_ID, "Authorization": f"Bearer {access_token}"}
    params = {"login": username}
    response = requests.get(BASE_URL + "users", headers=headers, params=params)
    response.raise_for_status()
    data = response.json()
    if data["data"]:
        return data["data"][0]["id"]
    else:
        raise ValueError(f"Utilisateur Twitch '{username}' introuvable.")

def get_clips(broadcaster_id, access_token, period="week", limit=5):
    headers = {"Client-ID": CLIENT_ID, "Authorization": f"Bearer {access_token}"}
    
    now = datetime.utcnow()
    if period == "stream":
        started_at = now - timedelta(hours=4)
    elif period == "week":
        started_at = now - timedelta(days=7)
    elif period == "month":
        started_at = now - timedelta(days=30)
    else:
        raise ValueError("Période invalide. Choisissez 'stream', 'week' ou 'month'.")
    
    params = {"broadcaster_id": broadcaster_id, "first": limit, "started_at": started_at.isoformat() + "Z"}
    response = requests.get(BASE_URL + "clips", headers=headers, params=params)
    response.raise_for_status()
    return response.json()["data"]

@app.route('/', methods=['GET', 'POST'])
def index():
    clips_data = []
    if request.method == 'POST':
        streamer_username = request.form['streamer']
        period = request.form['period']
        access_token = get_access_token()
        
        try:
            broadcaster_id = get_streamer_id(streamer_username, access_token)
            clips_data = get_clips(broadcaster_id, access_token, period=period)
        except Exception as e:
            return render_template('index.html', error=str(e))
    
    return render_template('index.html', clips=clips_data)

if __name__ == "__main__":
    app.run(debug=True)