from google_auth_oauthlib.flow import InstalledAppFlow
import json

flow = InstalledAppFlow.from_client_secrets_file(
    'client_secret_.json',
    scopes=['https://www.googleapis.com/auth/business.manage']
)
creds = flow.run_local_server(port=0)

token = {
    'token': creds.token,
    'refresh_token': creds.refresh_token,
    'token_uri': 'https://oauth2.googleapis.com/token',
    'client_id': creds.client_id,
    'client_secret': creds.client_secret,
    'scopes': ['https://www.googleapis.com/auth/business.manage']
}

with open('oauth_token.json', 'w') as f:
    json.dump(token, f, indent=2)

print('Token saved to oauth_token.json')