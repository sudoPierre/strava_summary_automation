from dotenv import load_dotenv
import os
import datetime
from stravalib import Client

load_dotenv()

STRAVA_ACCESS_TOKEN = os.getenv('STRAVA_ACCESS_TOKEN')
STRAVA_REFRESH_TOKEN = os.getenv('STRAVA_REFRSH_TOKEN')

client = Client(access_token=STRAVA_ACCESS_TOKEN, refresh_token=STRAVA_REFRESH_TOKEN)
athlete = client.get_athlete()
#activities = client.get_activities(after=(datetime.datetime.now() - datetime.timedelta(days=1)))
activities = client.get_activities(limit=2)

print (datetime.datetime.now())
print("Hello, {}. I know you run in {}".format(athlete.firstname, athlete.city))

for activity in activities:
    print(activity.distance)