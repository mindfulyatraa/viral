"""
YouTube Shorts Automation - Oddly Satisfying Reaction Videos
Author: Your Name
Description: Automatically creates reaction shorts with anti-copyright transformations
"""

import os
import random
import subprocess
import asyncio
from pathlib import Path
from moviepy.editor import (
    VideoFileClip, AudioFileClip, CompositeVideoClip, 
    CompositeAudioClip, TextClip, ColorClip
)
from moviepy.video.fx.all import mirror_x, colorx
import edge_tts
import argparse
import sys
from youtube_uploader import upload_video

# ==================== CONFIGURATION ====================
class Config:
    # Folders
    DOWNLOADS_FOLDER = "downloads"
    REACTIONS_FOLDER = "assets/reactions"
    MUSIC_FOLDER = "assets/music"
    OUTPUT_FOLDER = "output"
    TEMP_FOLDER = "temp"
    
    # Video dimensions (9:16 Vertical)
    CANVAS_WIDTH = 1080
    CANVAS_HEIGHT = 1920
    
    # Template Configuration (Based on User Image)
    # The reaction video is the "Template" (Full 1920x1080)
    # It has a "Black Part" at the bottom where the viral video goes.
    # Estimated from image: Face is top ~35-40%, Text is next 5%, Black is bottom ~55-60%
    
    CONTENT_ZONE_Y = 850      # Vertical start of the black area (approx 45% down)
    CONTENT_ZONE_HEIGHT = 1070 # Height of black area (1920 - 850)
    CONTENT_ZONE_WIDTH = 1080  # Full width
    
    # Effects
    BRIGHTNESS_FACTOR = 1.1
    SATURATION_FACTOR = 1.1
    MUSIC_VOLUME = 0.10
    
    # TTS Settings
    TTS_VOICE_HINDI = "hi-IN-SwaraNeural" 
    TTS_VOICE_ENGLISH = "en-IN-NeerjaNeural" 
    
    # Text overlay - Disabled since template has text, but kept for commentary
    TEXT_OPTIONS = [] 
    TEXT_COLOR = "yellow"
    TEXT_FONT = "Arial-Bold"
    TEXT_SIZE = 60

# ==================== UTILITY FUNCTIONS ====================
def create_folders():
    """Create necessary folders if they don't exist"""
    folders = [
        Config.DOWNLOADS_FOLDER,
        Config.REACTIONS_FOLDER,
        Config.MUSIC_FOLDER,
        Config.OUTPUT_FOLDER,
        Config.TEMP_FOLDER
    ]
    for folder in folders:
        Path(folder).mkdir(parents=True, exist_ok=True)
    print("✅ Folders created successfully")

def download_video(url, output_path):
    """Download video using yt-dlp with no watermark"""
    try:
        print(f"📥 Downloading video from: {url}")
        
        # yt-dlp command using python module to avoid PATH issues
        command = [
            sys.executable, "-m", "yt_dlp",
            "-f", "best",
            "--no-warnings",
            "--no-playlist",
            "-o", output_path,
            url
        ]
        
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        
        if os.path.exists(output_path):
            print(f"✅ Video downloaded: {output_path}")
            return output_path
        else:
            print("❌ Download failed - file not created")
            return None
            
    except subprocess.CalledProcessError as e:
        print(f"❌ yt-dlp error: {e.stderr}")
        return None
    except Exception as e:
        print(f"❌ Download error: {str(e)}")
        return None

def get_random_file(folder, extensions=[".mp4", ".mov", ".avi", ".mp3", ".wav", ".m4a"]):
    """Get random file from folder"""
    try:
        if not os.path.exists(folder):
             return None
        files = [f for f in os.listdir(folder) 
                if os.path.splitext(f)[1].lower() in extensions]
        
        if not files:
            # print(f"⚠️ No files found in {folder}") # Optional noise
            return None
            
        selected = random.choice(files)
        return os.path.join(folder, selected)
    except Exception as e:
        print(f"❌ Error reading folder {folder}: {str(e)}")
        return None

async def generate_voiceover(text, output_path, language="hindi"):
    """Generate TTS voiceover using edge-tts"""
    try:
        print(f"🎙️ Generating voiceover: {text[:50]}...")
        
        voice = Config.TTS_VOICE_HINDI if language == "hindi" else Config.TTS_VOICE_ENGLISH
        
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_path)
        
        print(f"✅ Voiceover saved: {output_path}")
        return output_path
    except Exception as e:
        print(f"❌ TTS error: {str(e)}")
        return None

# ==================== VIDEO PROCESSING ====================
def apply_anti_copyright_effects(video_clip):
    """Apply transformations to avoid copyright detection"""
    try:
        print("🎨 Applying anti-copyright effects...")
        video_clip = mirror_x(video_clip)
        video_clip = colorx(video_clip, Config.BRIGHTNESS_FACTOR)
        print("✅ Effects applied")
        return video_clip
    except Exception as e:
        print(f"❌ Effects error: {str(e)}")
        return video_clip

def resize_to_fit_zone(video_clip, zone_width, zone_height):
    """Resize video to fit INSIDE the boolean zone (like CSS object-fit: contain)"""
    try:
        # Calculate aspect ratios
        video_ratio = video_clip.w / video_clip.h
        zone_ratio = zone_width / zone_height
        
        if video_ratio > zone_ratio:
            # Video is wider than zone - fit to width
            new_width = zone_width
            new_height = int(zone_width / video_ratio)
        else:
            # Video is taller than zone - fit to height
            new_height = zone_height
            new_width = int(zone_height * video_ratio)
            
        video_clip = video_clip.resize(newsize=(new_width, new_height))
        
        # Center in zone
        x_offset = (zone_width - new_width) // 2
        y_offset = (zone_height - new_height) // 2
        
        return video_clip, x_offset, y_offset
    except Exception as e:
        print(f"❌ Resize error: {str(e)}")
        return video_clip, 0, 0

def process_video(source_video_path, reaction_video_path, music_path, 
                 voiceover_path, output_path):
    """Main video processing function"""
    try:
        print("\n" + "="*50)
        print("🎬 Starting video processing (Template Mode)...")
        print("="*50)
        
        # 1. Load the Reaction Template (The Base)
        print("📂 Loading reaction template...")
        template_clip = VideoFileClip(reaction_video_path)
        # Resize template to ensure it matches canvas if not already
        if template_clip.w != Config.CANVAS_WIDTH or template_clip.h != Config.CANVAS_HEIGHT:
             print(f"⚠️ Resizing template from {template_clip.size} to {Config.CANVAS_WIDTH}x{Config.CANVAS_HEIGHT}")
             template_clip = template_clip.resize(newsize=(Config.CANVAS_WIDTH, Config.CANVAS_HEIGHT))
        
        # 2. Load and Process Source Video (The Viral Content)
        print("📂 Loading source video...")
        source_clip = VideoFileClip(source_video_path)
        
        # Determine duration (Template dictates length usually, or shortest)
        min_duration = min(template_clip.duration, source_clip.duration, 60)
        
        # TRIM LOGIC: Keep the END of the template (User Request)
        if template_clip.duration > min_duration:
            start_time = template_clip.duration - min_duration
            template_clip = template_clip.subclip(start_time, template_clip.duration)
        else:
            template_clip = template_clip.subclip(0, min_duration)
            
        source_clip = source_clip.subclip(0, min_duration)
        
        # Apply anti-copyright to source ONLY
        source_clip = apply_anti_copyright_effects(source_clip)
        source_clip = source_clip.without_audio() # Usually remove source audio for voiceover
        
        # 3. Position Source Video in the "Black Zone"
        print("📐 Positioning video in black zone...")
        
        zone_w = Config.CONTENT_ZONE_WIDTH
        zone_h = Config.CONTENT_ZONE_HEIGHT
        
        # --- A. Create Background Fill (To hide black bars) ---
        # Resize to COVER the zone (fills gaps)
        bg_fill = source_clip.resize(height=zone_h)
        if bg_fill.w < zone_w:
            bg_fill = source_clip.resize(width=zone_w)
        
        # Center crop the background
        bg_fill = bg_fill.crop(x1=bg_fill.w/2 - zone_w/2, 
                             x2=bg_fill.w/2 + zone_w/2,
                             y1=bg_fill.h/2 - zone_h/2, 
                             y2=bg_fill.h/2 + zone_h/2)
                             
        # Darken background to make foreground pop
        bg_fill = colorx(bg_fill, 0.3) 
        bg_fill = bg_fill.set_position((0, Config.CONTENT_ZONE_Y))

        # --- B. Create Foreground Video (The main content) ---
        # Resize source to fit in the defined content zone (Contain)
        source_resized, x_off, y_off = resize_to_fit_zone(
            source_clip, 
            zone_w, 
            zone_h
        )
        
        # Calculate absolute position on canvas
        final_x = x_off 
        final_y = Config.CONTENT_ZONE_Y + y_off
        source_resized = source_resized.set_position((final_x, final_y))
        
        # 4. Composite
        # Order: Template -> Background Fill -> Foreground Source
        print("🎞️ Compositing final video...")
        final_video = CompositeVideoClip([
            template_clip,
            bg_fill,      # Fills the black hole
            source_resized # Fits perfectly on top
        ])
        
        # 5. Audio Processing
        print("🎵 Processing audio...")
        audio_clips = []
        
        # Keep Template Audio (The user's reaction sounds)? 
        # User didn't specify, but usually yes for reactions.
        if template_clip.audio:
            audio_clips.append(template_clip.audio)
            
        # Add generated voiceover
        if voiceover_path and os.path.exists(voiceover_path):
            voiceover = AudioFileClip(voiceover_path)
            audio_clips.append(voiceover)
        
        # Add background music
        if music_path and os.path.exists(music_path):
            music = AudioFileClip(music_path).subclip(0, min_duration)
            music = music.volumex(Config.MUSIC_VOLUME)
            audio_clips.append(music)
        
        # Composite audio
        if audio_clips:
            final_audio = CompositeAudioClip(audio_clips)
            final_video = final_video.set_audio(final_audio)
        
        # Export
        print("💾 Exporting final video...")
        final_video.write_videofile(
            output_path,
            fps=30,
            codec='libx264',
            audio_codec='aac',
            preset='medium',
            threads=4
        )
        
        # Clean up
        template_clip.close()
        source_clip.close()
        final_video.close()
        
        print("✅ Video processing completed!")
        print(f"📁 Output saved: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"❌ Processing error: {str(e)}")
        return None

# ==================== AUTOMATION LOGIC ====================
AUTO_COMMENTARIES = [
    "OMG look at this! So cute! Wait for it...",
    "This is the funniest thing I've seen today! 😂",
    "I simply cannot stop watching this. Too adorable!",
    "Wait for the end result! It's worth it.",
    "Tag a friend who needs to see this! 👇"
]

def auto_mode():
    """Run bot in fully autonomous mode for GitHub Actions"""
    try:
        print("🤖 STARTING AUTO MODE...")
        
        # 1. Acquire Content (Auto-Search)
        print("🔍 Searching for viral content...")
        # Removed "oddly satisfying pets" as it returns long compilations
        queries = ["funny cat shorts", "cute dog shorts", "funny pets reaction"]
        query = random.choice(queries)
        
        search_query = f"ytsearch5:{query}"
        download_path = os.path.join(Config.DOWNLOADS_FOLDER, "auto_video.mp4")
        
        # Custom download for search
        cmd = [
            sys.executable, "-m", "yt_dlp",
            "--match-filter", "duration < 59",
            "-o", download_path,
            "--no-playlist",
            "--max-downloads", "1",
            "--force-overwrites",
            search_query
        ]
        # check=False because yt-dlp returns non-zero when max-downloads is reached
        subprocess.run(cmd, check=False) 
        
        if not os.path.exists(download_path):
            print("❌ Auto-download failed")
            return
            
        # 1.5 Get Video Metadata (Advanced SEO)
        print("📊 Fetching metadata for Advanced SEO...")
        try:
            # Get JSON metadata for the downloaded video (or the search result)
            # We use the search query again to get info, or rely on file metadata if possible.
            # Best way: Use yt-dlp to dump json for the search query to capture Title/Tags
            meta_cmd = [
                sys.executable, "-m", "yt_dlp", 
                "--dump-json", 
                "--no-playlist",
                "--max-downloads", "1", 
                search_query
            ]
            meta_result = subprocess.run(meta_cmd, capture_output=True, text=True, check=False)
            import json
            video_info = json.loads(meta_result.stdout.split('\n')[0]) # First line is usually the json
            
            source_title = video_info.get('title', query.title())
            source_tags = video_info.get('tags', [])
            
            print(f"✅ Source Title: {source_title}")
        except Exception as e:
            print(f"⚠️ Metadata fetch failed: {e}. Using generic SEO.")
            source_title = query.title()
            source_tags = []

        # 2. Select Assets
        reaction_video = get_random_file(Config.REACTIONS_FOLDER)
        if not reaction_video:
            print("❌ No reactions found for auto mode")
            return
            
        music_file = get_random_file(Config.MUSIC_FOLDER)
        
        # 3. Commentary
        commentary = random.choice(AUTO_COMMENTARIES)
        voiceover_path = os.path.join(Config.TEMP_FOLDER, "voiceover.mp3")
        asyncio.run(generate_voiceover(commentary, voiceover_path, "english"))
        
        # 4. Process
        output_filename = f"shorts_auto_{random.randint(1000, 9999)}.mp4"
        output_path = os.path.join(Config.OUTPUT_FOLDER, output_filename)
        
        result_path = process_video(
            download_path,
            reaction_video,
            music_file,
            voiceover_path,
            output_path
        )
        
        # 5. Upload to YouTube (ADVANCED SEO)
        if result_path:
            print("🚀 Ready to upload...")
            
            # Smart Title Generation
            # "Reaction to [Source Title] - [Hook] #shorts"
            clean_source_title = source_title.split('#')[0].strip()[:50] # Clean up
            hooks = ['Wait for it!', 'Hilarious!', 'Too Cute!', 'Reaction']
            final_title = f"{clean_source_title} - {random.choice(hooks)} 😲 #shorts"
            
            # Smart Description
            description = (
                f"{commentary}\n\n"
                f"My reaction to this amazing video: {clean_source_title}\n\n"
                f"Subscribe for more satisfying and funny reactions!\n\n"
                f"#shorts #funny #pets #reaction #viral { ' '.join(['#'+t.replace(' ','') for t in source_tags[:5]]) }"
            )
            
            # Smart Tags
            base_tags = ["shorts", "funny", "pets", "reaction", "viral", "trending"]
            combined_tags = list(set(base_tags + source_tags[:10])) # Unique tags
            
            print(f"📝 Title: {final_title}")
            upload_video(result_path, final_title, description, combined_tags)
            
    except Exception as e:
        print(f"❌ Auto Mode Error: {str(e)}")

# ==================== MAIN WORKFLOW ====================
def main():
    """Main execution function"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--auto", action="store_true", help="Run in fully automated mode")
    args = parser.parse_args()

    # Create folders
    create_folders()

    # Dispatch to Auto Mode
    if args.auto:
        auto_mode()
        return

    # MANUAL MODE
    print("\n" + "="*60)
    print("🎥 YouTube Shorts Automation - Pet Reactions (Funny/Cute)")
    print("="*60 + "\n")
    
    # Get user input
    print("\n📝 Enter video details:")
    print("💡 Tip: Use 'Funny Pet Shorts' or 'Cute Cat Reaction' videos.")
    video_url = input("Video URL (Douyin/Bilibili/YouTube Shorts): ").strip()
    
    if not video_url:
        print("❌ No URL provided. Using demo mode...")
        video_url = None
    
    # Commentary script
    print("\n📝 Enter commentary (Hindi/English):")
    print("Example: 'Dekho ye kitna satisfying hai! Wait for the end.'")
    commentary = input("Commentary: ").strip()
    
    if not commentary:
        commentary = "Dekho ye kitna amazing hai! Ye reaction dekhke maja aa jayega. Wait for it!"
    
    language = input("Language (hindi/english) [hindi]: ").strip().lower() or "hindi"
    
    # Download video
    downloaded_video = None
    if video_url:
        download_path = os.path.join(Config.DOWNLOADS_FOLDER, "source_video.mp4")
        downloaded_video = download_video(video_url, download_path)
        if not downloaded_video:
            print("❌ Download failed. Exiting...")
            return
    else:
        existing_videos = [f for f in os.listdir(Config.DOWNLOADS_FOLDER) 
                          if f.endswith(('.mp4', '.mov', '.avi'))]
        if existing_videos:
            downloaded_video = os.path.join(Config.DOWNLOADS_FOLDER, existing_videos[0])
            print(f"✅ Using existing video: {downloaded_video}")
        else:
            print("❌ No video found.")
            return
    
    # Assets
    reaction_video = get_random_file(Config.REACTIONS_FOLDER)
    if not reaction_video:
        print("❌ No reaction videos found.")
        return
    print(f"🎭 Selected reaction: {os.path.basename(reaction_video)}")
    
    music_file = get_random_file(Config.MUSIC_FOLDER)
    if music_file:
         print(f"🎵 Selected music: {os.path.basename(music_file)}")
    
    # Generate voiceover
    voiceover_path = os.path.join(Config.TEMP_FOLDER, "voiceover.mp3")
    print("\n🎙️ Generating voiceover...")
    asyncio.run(generate_voiceover(commentary, voiceover_path, language))
    
    # Process video
    output_filename = f"shorts_{random.randint(1000, 9999)}.mp4"
    output_path = os.path.join(Config.OUTPUT_FOLDER, output_filename)
    
    result = process_video(
        downloaded_video,
        reaction_video,
        music_file,
        voiceover_path,
        output_path
    )
    
    if result:
        print("\n" + "="*60)
        print("🎉 SUCCESS! Your video is ready!")
        print(f"📁 Location: {result}")
        print("="*60 + "\n")
        
        # Manual Upload Prompt
        upload = input("🚀 Upload to YouTube? (y/n): ").lower()
        if upload == 'y':
            title = input("📝 Title: ")
            desc = input("📝 Description: ")
            tags = ["shorts", "reaction", "funny"]
            upload_video(result, title, desc, tags)
    else:
        print("\n❌ Video creation failed.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Process interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
