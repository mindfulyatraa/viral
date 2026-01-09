import os
import time
import json
import logging
from datetime import datetime, timedelta
import requests
from pathlib import Path
import random

# Video processing libraries
from moviepy.editor import VideoFileClip, concatenate_videoclips, CompositeVideoClip, ImageClip
from moviepy.video.fx.resize import resize
from PIL import Image, ImageDraw, ImageFont
import yt_dlp
import imageio_ffmpeg
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('viral_bot.log'),
        logging.StreamHandler()
    ]
)

class ViralVideoBot:
    def __init__(self, config_path='config.json'):
        """Initialize bot with configuration"""
        self.config = self.load_config(config_path)
        self.processed_videos = self.load_processed_list()
        self.reaction_videos = self.get_reaction_videos()
        self.youtube_uploader = None
        self.ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
        
        # Initialize YouTube uploader if enabled
        if 'youtube' in self.config.get('upload_platforms', []):
            try:
                from youtube_uploader import YouTubeUploader
                self.youtube_uploader = YouTubeUploader()
                logging.info("YouTube uploader initialized")
            except Exception as e:
                logging.warning(f"YouTube uploader not available: {e}")
        
    def load_config(self, config_path):
        """Load configuration from JSON file"""
        default_config = {
            "search_keywords": [
                "funny pets", "viral funny", "cute animals",
                "unexpected", "hilarious", "comedy gold"
            ],
            "min_views": 100000,
            "max_video_duration": 60,
            "check_interval_minutes": 30,
            "output_dir": "output_videos",
            "reaction_dir": "reaction_videos",
            "upload_platforms": ["youtube", "tiktok"],
            "reddit_subreddits": ["funny", "aww", "unexpected", "PublicFreakout"],
            "video_quality": "720p"
        }
        
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        else:
            with open(config_path, 'w') as f:
                json.dump(default_config, f, indent=4)
                
        return default_config
    
    def load_processed_list(self):
        """Load list of already processed videos"""
        processed_file = 'processed_videos.json'
        if os.path.exists(processed_file):
            with open(processed_file, 'r') as f:
                return json.load(f)
        return []
    
    def save_processed_list(self):
        """Save processed videos list"""
        with open('processed_videos.json', 'w') as f:
            json.dump(self.processed_videos, f, indent=4)
    
    def get_reaction_videos(self):
        """Get list of available reaction videos"""
        reaction_dir = Path(self.config['reaction_dir'])
        if not reaction_dir.exists():
            reaction_dir.mkdir(parents=True)
            logging.warning(f"Reaction directory created: {reaction_dir}")
            return []
        
        reactions = list(reaction_dir.glob("*.mp4"))
        logging.info(f"Found {len(reactions)} reaction videos")
        return [str(r) for r in reactions]
    
    def search_viral_videos_reddit(self):
        """Search for viral videos on Reddit"""
        viral_videos = []
        
    def search_viral_videos_reddit(self):
        """Search for viral videos on Reddit using RSS feeds (Direct DASH URL extraction)"""
        viral_videos = []
        import xml.etree.ElementTree as ET
        import re
        
        for subreddit in self.config['reddit_subreddits']:
            try:
                # Use RSS feed
                url = f"https://www.reddit.com/r/{subreddit}/top/.rss?t=day&limit=10"
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'application/xml,application/atom+xml,text/html,*/*;q=0.9'
                }
                
                response = requests.get(url, headers=headers, timeout=15)
                
                if response.status_code == 200:
                    try:
                        root = ET.fromstring(response.text)
                        
                        # Handle namespaces
                        namespace = {'atom': 'http://www.w3.org/2005/Atom'} 
                        entries = root.findall('atom:entry', namespace)
                        if not entries:
                            entries = root.findall('{http://www.w3.org/2005/Atom}entry')
                            
                        for entry in entries:
                            # Extract Title
                            title_elem = entry.find('atom:title', namespace)
                            if title_elem is None:
                                title_elem = entry.find('{http://www.w3.org/2005/Atom}title')
                            title = title_elem.text if title_elem is not None else "Viral Video"
                            
                            # Extract Link (href attribute)
                            link_elem = entry.find('atom:link', namespace)
                            if link_elem is None:
                                link_elem = entry.find('{http://www.w3.org/2005/Atom}link')
                                
                            permalink = link_elem.attrib.get('href', '') if link_elem is not None else ''
                            
                            # Extract Direct URL from Content
                            direct_url = None
                            content_elem = entry.find('atom:content', namespace)
                            if content_elem is None:
                                content_elem = entry.find('{http://www.w3.org/2005/Atom}content')
                            
                            if content_elem is not None and content_elem.text:
                                # Look for v.redd.it links
                                video_match = re.search(r'https://v\.redd\.it/([a-zA-Z0-9]+)', content_elem.text)
                                if video_match:
                                    video_id = video_match.group(1)
                                    # Construct DASH URL (try 720p)
                                    direct_url = f'https://v.redd.it/{video_id}/DASH_720.mp4'
                            
                            if direct_url:
                                video_info = {
                                    'id': video_id,
                                    'title': title,
                                    'url': permalink,
                                    'direct_url': direct_url,
                                    'score': 10000, 
                                    'source': 'reddit',
                                    'subreddit': subreddit
                                }
                                
                                if video_info['id'] not in self.processed_videos:
                                    viral_videos.append(video_info)
                                    logging.info(f"Found viral video: {title[:50]}... (Direct URL)")
                                    
                    except ET.ParseError as e:
                        logging.error(f"Error parsing RSS XML for r/{subreddit}: {e}")
                else:
                    logging.warning(f"Reddit RSS access failed: {response.status_code}")
                time.sleep(2)
            except Exception as e:
                logging.error(f"Error searching Reddit r/{subreddit}: {str(e)}")
        
        return viral_videos
        
        return viral_videos

    def search_viral_videos_youtube(self):
        """Search for viral Shorts on YouTube (USA Region)"""
        if not self.youtube_uploader or not self.youtube_uploader.youtube:
            logging.error("YouTube API not initialized. Cannot search videos.")
            return []
            
        logging.info("Searching YouTube for viral Shorts in USA...")
        video_list = []
        
        try:
            # 1. Search for popular videos in US
            request = self.youtube_uploader.youtube.search().list(
                part="snippet",
                maxResults=20,
                q="viral shorts",
                regionCode=self.config.get('youtube_region', 'US'),
                type="video",
                videoDuration="short",  # Filter for potential Shorts (< 4 mins)
                order="viewCount",      # Get most viewed
                relevanceLanguage="en"
            )
            response = request.execute()
            
            for item in response.get('items', []):
                video_limit = 5 # Process max 5 videos per run
                if len(video_list) >= video_limit:
                    break
                    
                video_id = item['id']['videoId']
                
                # Check if already processed
                if video_id in self.processed_videos:
                    continue
                
                # Get video details (to check actual duration and view count)
                vid_request = self.youtube_uploader.youtube.videos().list(
                    part="contentDetails,statistics,snippet",
                    id=video_id
                )
                vid_response = vid_request.execute()
                
                if not vid_response.get('items'):
                    continue
                    
                details = vid_response['items'][0]
                
                # Verify it's a Short (< 60s)
                # We rely on search(videoDuration='short') and our internal trimming
                # Removing strict ISO parsing to handle PT1M correctly
                
                view_count = int(details['statistics'].get('viewCount', 0))
                if view_count < self.config['min_views']:
                    continue
                
                # Add to list
                video_info = {
                    'id': video_id,
                    'url': f"https://www.youtube.com/watch?v={video_id}",
                    'title': details['snippet']['title'],
                    'author': details['snippet']['channelTitle'],
                    'views': view_count,
                    'source': 'youtube'
                }
                
                video_list.append(video_info)
                logging.info(f"Found viral video: {video_info['title']} ({video_info['views']} views)")
                
        except Exception as e:
            logging.error(f"Error searching YouTube: {e}")
            
        return video_list
    
    def download_video(self, video_info, output_path):
        """Direct download without yt-dlp - works on GitHub Actions"""
        import subprocess
        
        try:
            # Handle YouTube videos separately if needed (using yt-dlp for YT is fine)
            if 'youtube.com' in video_info.get('url', '') or 'youtu.be' in video_info.get('url', ''):
                # Use existing yt-dlp logic for YouTube ONLY
                logging.info("YouTube video detected, using yt-dlp...")
                ydl_opts = {
                    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                    'outtmpl': output_path,
                    'quiet': True,
                    'ffmpeg_location': self.ffmpeg_path,
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([video_info['url']])
                return os.path.exists(output_path)

            direct_url = video_info.get('direct_url')
            if not direct_url and 'v.redd.it' in video_info.get('url', ''):
                # Fallback: if we just have a v.redd.it url but not the DASH url
                direct_url = video_info['url']
                if not direct_url.endswith('.mp4'):
                     direct_url += '/DASH_720.mp4'

            if not direct_url:
                logging.error("No direct URL found for Reddit video")
                return False
            
            logging.info(f"Direct download from: {direct_url}")
            
            # Setup headers to mimic browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'video/webm,video/ogg,video/*;q=0.9,application/ogg;q=0.7,audio/*;q=0.6,*/*;q=0.5',
                'Accept-Language': 'en-US,en;q=0.5',
                'Range': 'bytes=0-',
                'Referer': 'https://www.reddit.com/',
                'Origin': 'https://www.reddit.com'
            }
            
            # Create session with retries
            session = requests.Session()
            adapter = requests.adapters.HTTPAdapter(max_retries=3)
            session.mount('http://', adapter)
            session.mount('https://', adapter)
            
            # Download video stream
            logging.info("Starting download...")
            response = session.get(direct_url, headers=headers, stream=True, timeout=60)
            
            if response.status_code in [200, 206]:
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk: f.write(chunk)
                
                # Download Audio
                audio_url = direct_url.replace('DASH_720.mp4', 'DASH_audio.mp4')
                # Handle generic replacement if 720 not in name
                if 'DASH_audio.mp4' not in audio_url:
                     audio_url = direct_url.rsplit('/', 1)[0] + '/DASH_audio.mp4'

                audio_path = str(output_path).replace('.mp4', '_audio.mp4')
                
                try:
                    logging.info(f"Downloading audio: {audio_url}")
                    audio_res = session.get(audio_url, headers=headers, stream=True, timeout=30)
                    
                    if audio_res.status_code == 200:
                        with open(audio_path, 'wb') as f:
                            for chunk in audio_res.iter_content(chunk_size=8192):
                                if chunk: f.write(chunk)
                        
                        logging.info("Merging audio...")
                        temp_output = str(output_path).replace('.mp4', '_merged.mp4')
                        
                        # Merge using ffmpeg
                        cmd = [
                            self.ffmpeg_path, '-i', output_path, '-i', audio_path,
                            '-c:v', 'copy', '-c:a', 'aac', '-strict', 'experimental',
                            '-y', temp_output
                        ]
                        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        
                        # Replace
                        if os.path.exists(temp_output):
                            os.remove(output_path)
                            os.rename(temp_output, output_path)
                            os.remove(audio_path)
                            logging.info("Merge successful")
                    else:
                        logging.warning("No audio track found")
                        
                except Exception as e:
                    # Non-fatal audio error
                    logging.warning(f"Audio merge failed: {e}")
                    if os.path.exists(audio_path): os.remove(audio_path)
                
                return True
                
            elif response.status_code == 403:
                logging.error("403 Forbidden on direct download. Trying FFmpeg with HLS Playlist...")
                
                # Fallback: Use FFmpeg to download HLS stream directly
                # This bypasses direct file blocks and handles the playlist
                if 'v.redd.it' in direct_url:
                    try:
                        # Construct HLS URL (base check)
                        base_url = direct_url.split('/DASH')[0]
                        hls_url = f"{base_url}/HLSPlaylist.m3u8"
                        
                        logging.info(f"Attempting HLS download via FFmpeg: {hls_url}")
                        
                        cmd = [
                            self.ffmpeg_path, '-i', hls_url,
                            '-c', 'copy', '-bsf:a', 'aac_adtstoasc',
                            '-y', output_path
                        ]
                        
                        # Run ffmpeg (mimicking a browser via headers if possible, but ffmpeg supports limited headers)
                        # We rely on ffmpeg's native HLS handling.
                        # Sometimes adding user-agent to ffmpeg helps: -user_agent "..."
                        cmd.extend(['-user_agent', headers['User-Agent']])
                        
                        result = subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
                        
                        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                            logging.info(f"✓ HLS Download successful: {output_path}")
                            return True
                    except subprocess.CalledProcessError as e:
                        logging.error(f"FFmpeg HLS download failed: {e.stderr}")
                    except Exception as e:
                        logging.error(f"HLS fallback error: {e}")
                
                return False
            else:
                logging.error(f"Download failed: {response.status_code}")
                return False

        except Exception as e:
            logging.error(f"Download error: {str(e)}")
            return False
    
    def create_text_overlay(self, duration, width, height):
        """Create text overlay with 'Wait for it...' on a black bar between videos"""
        try:
            # Fixed text
            caption_text = "Wait for it..."
            reaction_split_point = int(height * 0.4)  # 512px point
            
            # Create black strip image
            # Width: full video width (720)
            # Height: 80 pixels
            strip_height = 80
            img = Image.new('RGBA', (width, strip_height), (0, 0, 0, 255))
            draw = ImageDraw.Draw(img)
            
            # Font settings
            try:
                # Use standard Arial
                font = ImageFont.truetype("arial.ttf", 50)
            except:
                font = ImageFont.load_default()
            
            # Get text size to center it in the strip
            bbox = draw.textbbox((0, 0), caption_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Center text in the black strip
            text_x = (width - text_width) // 2
            text_y = (strip_height - text_height) // 2 - 5 # Small adjustment
            
            # Draw simple white text
            draw.text((text_x, text_y), caption_text, font=font, fill='white')
            
            # Convert to moviepy clip
            img_array = np.array(img)
            txt_clip = ImageClip(img_array, duration=duration)
            
            # Position: Centered on the split line
            # y = 512 - (80/2) = 472
            y_pos = reaction_split_point - (strip_height // 2)
            txt_clip = txt_clip.set_position(('center', y_pos))
            
            logging.info("Text separator created successfully")
            return txt_clip
            
        except Exception as e:
            logging.error(f"Error creating text overlay: {str(e)}")
            return None
    
    def create_reaction_video(self, original_video_path, reaction_video_path, output_path):
        """Create reaction video with reaction on top, viral video on bottom, and text overlay"""
        try:
            logging.info("Creating reaction video...")
            
            # Load videos
            viral_video = VideoFileClip(original_video_path)
            reaction_video = VideoFileClip(reaction_video_path)
            
            # Limit viral video duration
            max_duration = min(viral_video.duration, self.config['max_video_duration'])
            viral_video = viral_video.subclip(0, max_duration)
            
            # Adjust reaction video to match viral video duration
            # Loop reaction video if it's shorter than viral video
            if reaction_video.duration < viral_video.duration:
                loops_needed = int(viral_video.duration / reaction_video.duration) + 1
                reaction_video = concatenate_videoclips([reaction_video] * loops_needed)
            
            # Trim reaction to match exact duration
            reaction_video = reaction_video.subclip(0, viral_video.duration)
            
            # Video dimensions (9:16 format for shorts)
            width = 720
            height = 1280
            
            # Calculate heights for split layout
            # Reaction on top (40%), viral video on bottom (60%)
            reaction_height = int(height * 0.4)
            viral_height = int(height * 0.6)
            
            # Resize videos
            reaction_resized = resize(reaction_video, width=width)
            reaction_resized = reaction_resized.resize(height=reaction_height)
            
            viral_resized = resize(viral_video, width=width)
            viral_resized = viral_resized.resize(height=viral_height)
            
            # Position videos
            # Reaction at top
            reaction_resized = reaction_resized.set_position(("center", 0))
            # Viral video at bottom
            viral_resized = viral_resized.set_position(("center", reaction_height))
            
            # Create text overlay
            text_overlay = self.create_text_overlay(viral_video.duration, width, height)
            
            # Composite final video (order matters: bottom to top)
            clips = [reaction_resized, viral_resized]
            if text_overlay:
                clips.append(text_overlay)
            
            final = CompositeVideoClip(clips, size=(width, height))
            
            # Write output
            final.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                fps=30,
                preset='medium',
                threads=4
            )
            
            # Clean up
            viral_video.close()
            reaction_video.close()
            if text_overlay:
                text_overlay.close()
            final.close()
            
            logging.info(f"Reaction video created: {output_path}")
            return True
            
        except Exception as e:
            logging.error(f"Error creating reaction video: {str(e)}")
            return False
    
    def upload_video(self, video_path, video_info):
        """Upload video to platforms"""
        # NOTE: Actual upload implementation requires platform-specific APIs
        # This is a placeholder showing the structure
        
        for platform in self.config['upload_platforms']:
            try:
                if platform == 'youtube':
                    self.upload_to_youtube(video_path, video_info)
                elif platform == 'tiktok':
                    self.upload_to_tiktok(video_path, video_info)
                    
                logging.info(f"Uploaded to {platform}")
                
            except Exception as e:
                logging.error(f"Error uploading to {platform}: {str(e)}")
    
    def upload_to_youtube(self, video_path, video_info):
        """Upload to YouTube using YouTube API"""
        try:
            if not self.youtube_uploader:
                logging.warning("YouTube uploader not initialized")
                return False
            
            # Generate title and description
            title = self.youtube_uploader.generate_title(video_info['title'])
            description = self.youtube_uploader.generate_description(
                video_info['title'],
                video_info.get('subreddit')
            )
            
            # Upload video
            video_id = self.youtube_uploader.upload_video(
                video_path,
                title,
                description,
                tags=['shorts', 'viral', 'funny', 'reaction', 'trending']
            )
            
            if video_id:
                logging.info(f"Successfully uploaded to YouTube: {video_id}")
                return True
            else:
                logging.error("YouTube upload failed")
                return False
                
        except Exception as e:
            logging.error(f"Error in YouTube upload: {str(e)}")
            return False
    
    def upload_to_tiktok(self, video_path, video_info):
        """Upload to TikTok"""
        logging.info("TikTok upload would happen here")
        # Implementation requires TikTok API credentials
        pass
    
    def process_viral_video(self, video_info):
        """Process a single viral video"""
        try:
            # Create temp directory
            temp_dir = Path('temp')
            temp_dir.mkdir(exist_ok=True)
            
            # Download original video
            original_path = temp_dir / f"original_{video_info['id']}.mp4"
            if not self.download_video(video_info, original_path):
                return False
            
            # Select random reaction video
            if not self.reaction_videos:
                logging.error("No reaction videos available!")
                return False
            
            reaction_path = random.choice(self.reaction_videos)
            
            # Create output
            output_dir = Path(self.config['output_dir'])
            output_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = output_dir / f"reaction_{timestamp}.mp4"
            
            # Create reaction video
            if not self.create_reaction_video(str(original_path), reaction_path, str(output_path)):
                return False
            
            # Upload video
            self.upload_video(str(output_path), video_info)
            
            # Mark as processed
            self.processed_videos.append(video_info['id'])
            self.save_processed_list()
            
            # Cleanup temp files
            original_path.unlink()
            
            logging.info(f"Successfully processed video: {video_info['id']}")
            return True
            
        except Exception as e:
            logging.error(f"Error processing video: {str(e)}")
            return False
    
    def run(self):
        """Main bot loop - runs 24/7"""
        logging.info("Starting Viral Video Reaction Bot...")
        
        while True:
            try:
                logging.info("Searching for viral videos...")
                
                # Search for viral videos
                if self.config.get('source_platform') == 'youtube':
                    viral_videos = self.search_viral_videos_youtube()
                else:
                    viral_videos = self.search_viral_videos_reddit()
                
                logging.info(f"Found {len(viral_videos)} new viral videos")
                
                # Process each video
                for video_info in viral_videos:
                    success = self.process_viral_video(video_info)
                    
                    if success:
                        # Wait between processing to avoid rate limits
                        time.sleep(60)
                
                # Wait before next search cycle
                wait_minutes = self.config['check_interval_minutes']
                logging.info(f"Waiting {wait_minutes} minutes before next search...")
                time.sleep(wait_minutes * 60)
                
            except KeyboardInterrupt:
                logging.info("Bot stopped by user")
                break
            except Exception as e:
                logging.error(f"Unexpected error in main loop: {str(e)}")
                time.sleep(300)  # Wait 5 minutes on error


if __name__ == "__main__":
    # Create bot instance and run
    bot = ViralVideoBot()
    bot.run()
