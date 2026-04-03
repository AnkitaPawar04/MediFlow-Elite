"""Google Calendar integration service."""
import logging
import os
from datetime import datetime

from django.conf import settings
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/calendar']

CLIENT_SECRETS_FILE = os.path.join(
    settings.BASE_DIR, 'credentials.json'
)

def get_google_auth_url(user_id, state=None):
    print(">>> GOOGLE_REDIRECT_URI FROM SETTINGS:", settings.GOOGLE_REDIRECT_URI)

    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=settings.GOOGLE_REDIRECT_URI,
        state=state or str(user_id)
    )

    auth_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    return auth_url, state



def handle_oauth_callback(code, user):
    try:
        flow = Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE,
            scopes=SCOPES,
            redirect_uri=settings.GOOGLE_REDIRECT_URI
        )

        flow.fetch_token(code=code)
        credentials = flow.credentials

        user.google_calendar_token = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes,
        }
        user.save()

        logger.info(f"Google Calendar connected for {user.email}")
        return True

    except Exception as e:
        logger.exception("OAuth callback failed")
        return False


def create_calendar_event(user, booking):
    try:
        if not user.google_calendar_token:
            logger.warning(f"No Google token for {user.email}")
            return False

        token = user.google_calendar_token
        credentials = Credentials(
            token=token['token'],
            refresh_token=token.get('refresh_token'),
            token_uri=token['token_uri'],
            client_id=token['client_id'],
            client_secret=token['client_secret'],
            scopes=token['scopes']
        )

        if credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())

        service = build('calendar', 'v3', credentials=credentials)

        slot = booking.slot
        start = datetime.combine(slot.date, slot.start_time)
        end = datetime.combine(slot.date, slot.end_time)

        event = {
            'summary': 'Medical Appointment',
            'description': (
                f"Booking with {booking.doctor.get_full_name()}"
                if user.is_patient()
                else f"Appointment with {booking.patient.get_full_name()}"
            ),
            'start': {
                'dateTime': start.isoformat(),
                'timeZone': settings.TIME_ZONE,
            },
            'end': {
                'dateTime': end.isoformat(),
                'timeZone': settings.TIME_ZONE,
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 1440},
                    {'method': 'popup', 'minutes': 30},
                ]
            }
        }

        created_event = service.events().insert(
            calendarId='primary',
            body=event
        ).execute()

        logger.info(f"Calendar event created: {created_event['id']}")
        return True

    except Exception:
        logger.exception("Failed to create calendar event")
        return False
