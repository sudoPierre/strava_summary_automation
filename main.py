from dotenv import load_dotenv
from google import genai
import os
import datetime
import stravalib
import json
import time

load_dotenv()

STRAVA_TOKEN_FILE = 'strava_token.json'
STRAVA_CLIENT_ID = os.getenv('STRAVA_CLIENT_ID')
STRAVA_CLIENT_SECRET = os.getenv('STRAVA_CLIENT_SECRET')

client = stravalib.Client()
google_client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

def load_tokens():
    if os.path.exists(STRAVA_TOKEN_FILE):
        with open(STRAVA_TOKEN_FILE, 'r') as f:
            return json.load(f)
    return None

def save_tokens(token):
  with open(STRAVA_TOKEN_FILE, 'w') as f:
    json.dump(token, f)

tokens = load_tokens()

if not tokens:
    print("First connection...")
    print(f"1. Allez sur cette URL : https://www.strava.com/oauth/authorize?client_id={STRAVA_CLIENT_ID}&response_type=code&redirect_uri=http://localhost/exchange_token&approval_prompt=force&scope=activity:read_all")
    print("2. Autorisez l'app et copiez le paramètre 'code' dans l'URL de redirection.")
    
    code = input("Entrez le code ici : ")
    
    # Échange du code contre les jetons
    token_response = client.exchange_code_for_token(
        client_id=STRAVA_CLIENT_ID,
        client_secret=STRAVA_CLIENT_SECRET,
        code=code
    )
    save_tokens(token_response)
    tokens = token_response
    print("Jetons récupérés et sauvegardés avec succès !")

else:
    # CAS 2 : On a déjà des jetons, on vérifie s'il faut rafraîchir
    if time.time() > tokens['expires_at']:
        print("Token expiré, rafraîchissement automatique...")
        new_tokens = client.refresh_access_token(
            client_id=STRAVA_CLIENT_ID,
            client_secret=STRAVA_CLIENT_SECRET,
            refresh_token=tokens['refresh_token']
        )
        save_tokens(new_tokens)
        tokens = new_tokens
        print("Token rafraîchi !")

client.access_token = tokens['access_token']

def get_day_activities():
    activities = client.get_activities(after=(datetime.datetime.now() - datetime.timedelta(days=1)))
    activities.limit = 10
    activities_list = []
    for activity in activities:
        activities_list.append(activity.id)
    return activities_list

def format_activity_for_ai(activity):
    return {
        "id": activity.id,
        "date": activity.start_date_local.strftime("%Y-%m-%d %H:%M"),
        "nom": activity.name,
        "type": activity.type,
        "distance_km": round(float(activity.distance) / 1000, 2),
        "duree": activity.moving_time,
        "denivele_m": float(activity.total_elevation_gain),
        "vitesse_moyenne_kmh": round(float(activity.average_speed) * 3.6, 2)
    }

def get_activities_details():
    activities_details_list = []
    for current_activity_id in get_day_activities():
        activities_details_list.append(format_activity_for_ai(client.get_activity(current_activity_id)))
    return activities_details_list

def analyser_performances(data):
    # 1. Convertir la liste de dictionnaires en JSON String

    # 2. Construire un prompt structuré
    prompt = f"""
    ROLE:
    You are a friendly, expert running coach. 
    THE DATA IS ATTACHED BELOW IN JSON FORMAT. DO NOT IGNORE IT.

    JSON DATA:
    {data}
    
    INSTRUCTIONS:
    1. Start naturally as if you just opened the Strava notification (e.g., "Salut ! J'ai vu ta sortie de ce matin...").
    2. Analyze the latest activity by comparing it to the history (heart rate trends, pace, consistency).
    3. Use a supportive, "peer-to-peer" tone but provide high-level physiological insights.
    4. Mention at least two specific numbers from the data to show you've analyzed it.
    
    CONSTRAINTS:
    - LANGUAGE: Answer strictly in FRENCH.
    - TONE: Casual (use "Tu"), encouraging, and insightful. No corporate jargon.
    - Avoid saying "According to the JSON data". Act as if you simply KNOW the data.
    """

    # 3. Appel à l'API
    response = google_client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=prompt
    )
    print(prompt)
    return response.text

print(analyser_performances(get_activities_details()))

#print(get_activities_details())