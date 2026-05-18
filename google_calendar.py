# Google Calendar API integration module
import os
import json
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), 'google_credentials.json')
TOKEN_FILE = os.path.join(os.path.dirname(__file__), 'token.json')

def authenticate():
    credentials = None

    # Load saved token if exists
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r') as f:
            token_data = json.load(f)
        credentials = Credentials(
            token=token_data.get('token'),
            refresh_token=token_data.get('refresh_token'),
            token_uri=token_data.get('token_uri'),
            client_id=token_data.get('client_id'),
            client_secret=token_data.get('client_secret'),
            scopes=token_data.get('scopes')
        )

    # Refresh if expired
    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
        save_token(credentials)
        return credentials

    # If no valid credentials - run local auth flow
    if not credentials or not credentials.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            CREDENTIALS_FILE, SCOPES)
        credentials = flow.run_local_server(port=8502)
        save_token(credentials)

    return credentials

def save_token(credentials):
    token_data = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': list(credentials.scopes) if credentials.scopes else []
    }
    with open(TOKEN_FILE, 'w') as f:
        json.dump(token_data, f)

def load_credentials():
    if not os.path.exists(TOKEN_FILE):
        return None
    with open(TOKEN_FILE, 'r') as f:
        token_data = json.load(f)
    credentials = Credentials(
        token=token_data.get('token'),
        refresh_token=token_data.get('refresh_token'),
        token_uri=token_data.get('token_uri'),
        client_id=token_data.get('client_id'),
        client_secret=token_data.get('client_secret'),
        scopes=token_data.get('scopes')
    )
    if credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
        save_token(credentials)
    return credentials

def get_exercise_events_from_google(credentials):
    service = build('calendar', 'v3', credentials=credentials)
    now = datetime.utcnow()
    future = now + timedelta(days=90)

    events_result = service.events().list(
        calendarId='primary',
        timeMin=now.isoformat() + 'Z',
        timeMax=future.isoformat() + 'Z',
        maxResults=250,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])
    calendar_events = []
    exercise_events = []

    for event in events:
        title = event.get('summary', '')
        start_str = event['start'].get('dateTime', event['start'].get('date'))
        end_str = event['end'].get('dateTime', event['end'].get('date'))

        try:
            if 'T' in start_str:
                start = datetime.fromisoformat(start_str.replace('Z', '+00:00'))
                start = start.replace(tzinfo=None)
            else:
                start = datetime.strptime(start_str, '%Y-%m-%d')

            if 'T' in end_str:
                end = datetime.fromisoformat(end_str.replace('Z', '+00:00'))
                end = end.replace(tzinfo=None)
            else:
                end = datetime.strptime(end_str, '%Y-%m-%d')
        except:
            continue

        event_dict = {'title': title, 'start': start, 'end': end}
        calendar_events.append(event_dict)

        from csv_import import is_exercise_event
        if is_exercise_event(title):
            exercise_events.append(event_dict)

    return calendar_events, exercise_events

if __name__ == '__main__':
    print("Authenticating with Google Calendar...")
    credentials = authenticate()
    print("Authentication successful!")
    calendar_events, exercise_events = get_exercise_events_from_google(credentials)
    print(f"Total events: {len(calendar_events)}")
    print(f"Exercise events: {len(exercise_events)}")
    for event in exercise_events:
        print(f"  {event['title']} — {event['start']}")