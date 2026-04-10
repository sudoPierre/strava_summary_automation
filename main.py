from dotenv import load_dotenv
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

activities = client.get_activities(after=(datetime.datetime.now() - datetime.timedelta(days=1)))
#activities = client.get_activities()
activities.limit = 10
for activity in activities:
  print(f"Activity ID: {activity.id}")