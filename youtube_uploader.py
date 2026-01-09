import os
import pickle
import random
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Scopes required for uploading
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def get_authenticated_service():
    """Authenticate and return the YouTube service using pickle token"""
    creds = None
    # Load token if it exists
    if os.path.exists('youtube_token.pickle'):
        with open('youtube_token.pickle', 'rb') as token:
            creds = pickle.load(token)
            
    # Refresh if expired - this is critical for automation
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Refreshing access token...")
            creds.refresh(Request())
            # Save refreshed token
            with open('youtube_token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        else:
            # If no valid token, we can't automate without browser.
            # But the user claimed they have the files, so we assume it works.
            print("❌ No valid token found. Cannot upload automatically.")
            return None

    return build('youtube', 'v3', credentials=creds)

def upload_video(video_path, title, description, tags, category_id="23", privacy_status="public"):
    """Upload a video to YouTube"""
    try:
        if not os.path.exists(video_path):
            print(f"❌ Video file not found: {video_path}")
            return None

        youtube = get_authenticated_service()
        if not youtube:
            return None

        print(f"📤 Uploading: {title}...")
        
        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags,
                'categoryId': category_id
            },
            'status': {
                'privacyStatus': privacy_status,
                'selfDeclaredMadeForKids': False
            }
        }

        # MediaFileUpload handles large files better
        media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
        
        request = youtube.videos().insert(
            part=','.join(body.keys()),
            body=body,
            media_body=media
        )

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"🚀 Upload progress: {int(status.progress() * 100)}%")

        print(f"✅ Upload Complete! Video ID: {response['id']}")
        return response['id']

    except Exception as e:
        print(f"❌ Upload Failed: {str(e)}")
        return None

if __name__ == "__main__":
    # Test block
    print("Testing Auth...")
    service = get_authenticated_service()
    if service:
        print("✅ Auth Successful")
    else:
        print("❌ Auth Failed")
