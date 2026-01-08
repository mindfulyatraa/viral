"""
YouTube Upload Module
Handles authentication and video uploads to YouTube
"""

import os
import pickle
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import logging

# YouTube API scopes
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
TOKEN_FILE = 'youtube_token.pickle'
CREDENTIALS_FILE = 'client_secrets.json'

class YouTubeUploader:
    def __init__(self):
        self.youtube = None
        self.authenticate()
    
    def authenticate(self):
        """Authenticate with YouTube API"""
        creds = None
        
        # Check if we have saved credentials
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, 'rb') as token:
                creds = pickle.load(token)
        
        # If credentials don't exist or are invalid, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                logging.info("Refreshing YouTube credentials...")
                creds.refresh(Request())
            else:
                if not os.path.exists(CREDENTIALS_FILE):
                    logging.error(f"Credentials file not found: {CREDENTIALS_FILE}")
                    logging.error("Please download OAuth credentials from Google Cloud Console")
                    return False
                
                logging.info("Starting YouTube authentication flow...")
                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIALS_FILE, SCOPES)
                
                # Generate URL manually to print it
                auth_url, _ = flow.authorization_url(prompt='consent')
                
                print("\n" + "="*60)
                print("BROWSER OPEN NAHI HUA? YAHAN CLICK KARO:")
                print("="*60)
                print(auth_url)
                print("="*60 + "\n")
                
                logging.info("Waiting for authentication...")
                # Allow any port since localhost redirect handles it
                creds = flow.run_local_server(port=0)
            
            # Save credentials for future use
            with open(TOKEN_FILE, 'wb') as token:
                pickle.dump(creds, token)
            
            logging.info("YouTube authentication successful!")
        
        # Build YouTube service
        self.youtube = build('youtube', 'v3', credentials=creds)
        return True
    
    def upload_video(self, video_path, title, description, tags=None, category_id='24'):
        """
        Upload video to YouTube
        
        Args:
            video_path: Path to video file
            title: Video title
            description: Video description
            tags: List of tags (optional)
            category_id: YouTube category (24 = Entertainment)
        
        Returns:
            Video ID if successful, None otherwise
        """
        try:
            if not self.youtube:
                logging.error("YouTube API not authenticated")
                return None
            
            logging.info(f"Uploading video: {title}")
            
            # Default tags if not provided
            if tags is None:
                tags = ['shorts', 'viral', 'funny', 'reaction']
            
            # Video metadata
            body = {
                'snippet': {
                    'title': title[:100],  # Max 100 characters
                    'description': description[:5000],  # Max 5000 characters
                    'tags': tags[:500],  # Max 500 tags
                    'categoryId': category_id
                },
                'status': {
                    'privacyStatus': 'public',  # Can be: public, private, unlisted
                    'selfDeclaredMadeForKids': False
                }
            }
            
            # Create media upload
            media = MediaFileUpload(
                video_path,
                mimetype='video/mp4',
                resumable=True,
                chunksize=1024 * 1024  # 1MB chunks
            )
            
            # Execute upload
            request = self.youtube.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )
            
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    progress = int(status.progress() * 100)
                    logging.info(f"Upload progress: {progress}%")
            
            video_id = response['id']
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            
            logging.info(f"Upload successful!")
            logging.info(f"Video ID: {video_id}")
            logging.info(f"Video URL: {video_url}")
            
            return video_id
            
        except Exception as e:
            logging.error(f"Error uploading to YouTube: {str(e)}")
            return None
    
    def generate_title(self, original_title):
        """Generate catchy SEO-optimized YouTube title"""
        import re
        
        # 1. Clean up Reddit jargon
        clean_title = original_title
        # Remove [OC], (f), [m], etc.
        clean_title = re.sub(r'\[.*?\]', '', clean_title)
        clean_title = re.sub(r'\(.*?\)', '', clean_title)
        # Remove file extensions
        clean_title = re.sub(r'\.mp4|\.mov|\.mkv', '', clean_title, flags=re.IGNORECASE)
        # Remove common reddit phrases
        clean_title = clean_title.replace("reddit", "").replace("title", "").strip()
        
        # 2. Smart Truncation
        # YouTube max is 100 chars. We need space for " #Shorts" (8 chars) + hook (~20 chars)
        # So keep title around 60-70 chars
        if len(clean_title) > 65:
            clean_title = clean_title[:62] + "..."
            
        # 3. Add Engagement Hook
        hooks = [
            "Wait for it... 😂",
            "Unexpected! 😱",
            "So Satisfying 🤤",
            "Best Reaction! 🔥",
            "Hilarious 🤣",
            "Watch till end! 👀",
            "No way! 🤯"
        ]
        
        import random
        hook = random.choice(hooks)
        
        # 4. Construct Final Title
        # Format: "Video Title - Hook #Shorts"
        final_title = f"{clean_title} - {hook} #Shorts"
        
        # Final safety check for length
        if len(final_title) > 100:
            # If too long, drop the hook, keep title + #Shorts
            final_title = f"{clean_title} #Shorts"
            
        return final_title
    
    def generate_description(self, original_title, subreddit=None):
        """Generate SEO-rich YouTube description"""
        desc = f"{original_title}\n\n"
        desc += "👇 SUBSCRIBE FOR MORE REACTIONS 👇\n"
        desc += "https://www.youtube.com/channel/UCxxxxxxxx?sub_confirmation=1\n\n"
        
        desc += "🔥 The funniest viral videos and reactions daily! \n"
        desc += "Don't forget to like, comment and subscribe if you laughed! 😂\n\n"
        
        if subreddit:
            desc += f"Credit/Source: r/{subreddit}\n\n"
        
        # SEO Keywords block
        desc += "Ignore tags:\n"
        desc += "funny videos, viral reaction, best fails, comedy shorts, \n"
        desc += "tiktok trends, reddit top posts, funny animals, cute pets, \n"
        desc += "try not to laugh, reaction video, viral shorts 2024\n\n"
        
        desc += "#Shorts #Viral #Funny #Reaction #Comedy #Trending #Fails #Reddit\n"
        desc += "\n⚠️ fair use copyright disclaimer:\n"
        desc += "Copyright Disclaimer Under Section 107 of the Copyright Act 1976, allowance is made for 'fair use' for purposes such as criticism, commenting, news reporting, teaching, scholarship, and research. Fair use is a use permitted by copyright statute that might otherwise be infringing."
        
        return desc


# Test function
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    uploader = YouTubeUploader()
    
    # Test with demo video
    demo_video = Path("output_videos/DEMO_reaction.mp4")
    
    if demo_video.exists():
        print("\nTest upload to YouTube:")
        print(f"Video: {demo_video}")
        print("\nWARNING: This will upload to YouTube!")
        choice = input("Continue? (yes/no): ")
        
        if choice.lower() == 'yes':
            video_id = uploader.upload_video(
                str(demo_video),
                "Wait For It... 😂 #Shorts",
                "Viral reaction video compilation!\n\n#Shorts #Viral #Funny",
                tags=['shorts', 'viral', 'funny', 'reaction', 'comedy']
            )
            
            if video_id:
                print(f"\n✅ Upload successful!")
                print(f"Watch at: https://www.youtube.com/watch?v={video_id}")
            else:
                print("\n❌ Upload failed")
    else:
        print("Demo video not found. Create one first with: py quick_demo.py")
