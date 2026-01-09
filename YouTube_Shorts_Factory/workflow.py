"""
=================================================================================
COMPLETE YOUTUBE SHORTS AUTOMATION WORKFLOW
=================================================================================
Features:
1. Safe Viral Music Downloader (NCS, Audio Library, Vlog Music)
2. Auto License Credit Extractor
3. Video Processing with Anti-Copyright
4. Batch Processing Support
5. Professional Folder Organization
6. Auto Upload to YouTube
7. Original Audio Preservation (Source + Reaction)
=================================================================================
"""

import os
import re
import json
import random
import subprocess
import asyncio
from pathlib import Path
from datetime import datetime
from moviepy.editor import (
    VideoFileClip, AudioFileClip, CompositeVideoClip, 
    CompositeAudioClip, TextClip, ColorClip
)
from moviepy.video.fx.all import mirror_x, colorx
import edge_tts
import yt_dlp
from youtube_uploader import upload_video

# ==================== CONFIGURATION ====================
class Config:
    # Main Folders
    PROJECT_ROOT = "." 
    DOWNLOADS_FOLDER = os.path.join(PROJECT_ROOT, "downloads")
    REACTIONS_FOLDER = os.path.join(PROJECT_ROOT, "assets", "reactions")
    MUSIC_FOLDER = os.path.join(PROJECT_ROOT, "assets", "music")
    OUTPUT_FOLDER = os.path.join(PROJECT_ROOT, "output")
    TEMP_FOLDER = os.path.join(PROJECT_ROOT, "temp")
    CREDITS_FOLDER = os.path.join(PROJECT_ROOT, "credits")
    
    # Video Settings
    CANVAS_WIDTH = 1080
    CANVAS_HEIGHT = 1920
    REACTION_HEIGHT = int(CANVAS_HEIGHT * 0.40)  # Top 40%
    MAIN_VIDEO_HEIGHT = int(CANVAS_HEIGHT * 0.60)  # Bottom 60%
    
    # Anti-Copyright Effects
    BRIGHTNESS_FACTOR = 1.1
    MUSIC_VOLUME = 0.30  # 30% Volume
    MAX_VIDEO_DURATION = 58  # Shorts limit
    
    # TTS Settings (Disabled for now)
    TTS_VOICES = {
        "hindi": "hi-IN-SwaraNeural",
        "english": "en-IN-NeerjaNeural",
        "hinglish": "hi-IN-SwaraNeural"
    }
    
    # Text Overlays
    TEXT_PRESETS = {
        "hindi": ["इंतज़ार करो 🔥", "देखो क्या होगा 👀", "अमेजिंग! 😱", "Wait for it! ✨"],
        "english": ["Wait for it... 🔥", "Watch this! 👀", "Amazing! 😱", "So Satisfying ✨"],
        "hinglish": ["Wait karo yaar 🔥", "Dekho kya hoga 👀", "Ekdum zabardast! 😱", "Full satisfying hai 🌟"]
    }
    
    # Trusted Music Sources
    TRUSTED_MUSIC_SOURCES = [
        "NoCopyrightSounds trending",
        "Audio Library No Copyright Music popular",
        "Vlog No Copyright Music viral",
        "Chillhop Music lofi",
        "LAKEY INSPIRED beats"
    ]

# ==================== FOLDER SETUP ====================
def create_project_structure():
    """Create complete project folder structure"""
    folders = [
        Config.DOWNLOADS_FOLDER,
        Config.REACTIONS_FOLDER,
        Config.MUSIC_FOLDER,
        Config.OUTPUT_FOLDER,
        Config.TEMP_FOLDER,
        Config.CREDITS_FOLDER
    ]
    
    for folder in folders:
        Path(folder).mkdir(parents=True, exist_ok=True)
    
    # Create README files
    create_readme_files()

def create_readme_files():
    """Create helpful README files in each folder"""
    readme_content = {
        Config.REACTIONS_FOLDER: "📹 Place your reaction videos here (MP4/MOV format)\nIdeal: 15-60 seconds, Portrait mode (9:16)",
        Config.MUSIC_FOLDER: "🎵 Your downloaded background music will be saved here",
        Config.DOWNLOADS_FOLDER: "📥 Downloaded source videos are stored here temporarily",
        Config.OUTPUT_FOLDER: "🎬 Final processed videos are saved here",
        Config.CREDITS_FOLDER: "📄 Music credits and license info stored here"
    }
    
    for folder, content in readme_content.items():
        readme_path = os.path.join(folder, "README.txt")
        if not os.path.exists(readme_path):
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(content)

# ==================== MUSIC DOWNLOADER MODULE ====================
class SafeMusicDownloader:
    """Download safe viral music with auto credit extraction"""
    
    def __init__(self):
        self.music_folder = Config.MUSIC_FOLDER
        self.credits_folder = Config.CREDITS_FOLDER
    
    def extract_credits(self, description, title):
        credits_text = f"🎵 MUSIC CREDITS FOR: {title}\n"
        credits_text += "="*60 + "\n\n"
        patterns = [
            r"Music provided by.*", r"Track:.*", r"Artist:.*", r"Download.*",
            r"Stream.*", r"License.*", r"Creative Commons.*", r"Attribution.*"
        ]
        found_credits = []
        for pattern in patterns:
            matches = re.findall(pattern, description, re.IGNORECASE | re.MULTILINE)
            found_credits.extend(matches)
        
        if found_credits:
            credits_text += "\n".join(found_credits)
        else:
            credits_text += description[:500] + "..."
        
        credits_text += "\n\n" + "="*60
        credits_text += "\n⚠️ Copy above text to your YouTube video description!\n"
        return credits_text
    
    def download_music(self, num_songs=3, source_index=0):
        try:
            print(f"\n🎵 SAFE VIRAL MUSIC DOWNLOADER")
            source = Config.TRUSTED_MUSIC_SOURCES[source_index]
            print(f"📻 Source: {source}")
            
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(self.music_folder, '%(title)s.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'noplaylist': True,
                'quiet': False,
                'no_warnings': True,
                'ignoreerrors': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                search_query = f"ytsearch{num_songs}:{source}"
                info = ydl.extract_info(search_query, download=True)
                if 'entries' in info:
                    for entry in info['entries']:
                        if entry:
                            self.save_credits(entry)
            print(f"\n✅ Music download complete!")
            
        except Exception as e:
            print(f"❌ Music download error: {str(e)}")
    
    def save_credits(self, video_info):
        try:
            title = video_info.get('title', 'Unknown')
            description = video_info.get('description', '')
            credits = self.extract_credits(description, title)
            safe_filename = re.sub(r'[^\w\s-]', '', title)[:50]
            credits_file = os.path.join(self.credits_folder, f"{safe_filename}_credits.txt")
            with open(credits_file, 'w', encoding='utf-8') as f:
                f.write(credits)
        except Exception as e:
            print(f"⚠️ Credits save error: {str(e)}")

# ==================== VIDEO DOWNLOADER ====================
def download_video(url, output_path):
    try:
        print(f"\n📥 Downloading video from: {url}")
        command = [
            "yt-dlp", "-f", "best[height<=1080]", "--no-warnings", "-o", output_path, url
        ]
        subprocess.run(command, capture_output=True, text=True)
        
        if os.path.exists(output_path):
             return output_path
        
        base_name = os.path.splitext(output_path)[0]
        for ext in ['.mp4', '.mkv', '.webm']:
            if os.path.exists(base_name + ext):
                return base_name + ext
        return None
    except Exception as e:
        print(f"❌ Download error: {str(e)}")
        return None

# ==================== VIDEO PROCESSING ====================
def apply_anti_copyright_effects(video_clip):
    try:
        video_clip = mirror_x(video_clip)
        video_clip = colorx(video_clip, Config.BRIGHTNESS_FACTOR)
        return video_clip
    except Exception as e:
        return video_clip

def resize_and_position_video(video_clip, target_width, target_height, y_position, fit_mode="contain"):
    try:
        aspect_ratio = video_clip.w / video_clip.h
        target_aspect = target_width / target_height
        
        if fit_mode == "contain":
            if aspect_ratio > target_aspect:
                new_width = target_width
                new_height = int(target_width / aspect_ratio)
            else:
                new_height = target_height
                new_width = int(target_height * aspect_ratio)
        elif fit_mode == "cover":
            if aspect_ratio > target_aspect:
                new_height = target_height
                new_width = int(target_height * aspect_ratio)
            else:
                new_width = target_width
                new_height = int(target_width / aspect_ratio)
        
        video_clip = video_clip.resize(newsize=(new_width, new_height))
        x_position = (target_width - new_width) // 2
        y_offset = (target_height - new_height) // 2
        video_clip = video_clip.set_position((x_position, y_position + y_offset))
        return video_clip
    except Exception as e:
        return video_clip

def create_text_overlay(text, duration):
    try:
        txt_clip = TextClip(
            text, fontsize=65, color='yellow', font='Arial-Bold', 
            stroke_color='black', stroke_width=3, method='caption', 
            size=(Config.CANVAS_WIDTH - 100, None)
        )
        txt_clip = txt_clip.set_position('center').set_duration(duration)
        txt_clip = txt_clip.crossfadein(0.5).crossfadeout(0.5)
        return txt_clip
    except Exception as e:
        print(f"⚠️ Text overlay skipped (ImageMagick?): {e}")
        return None

async def generate_voiceover(text, output_path, language="hindi"):
    """
    Deprecated: Voiceover disabled as per user request (Original Audio Mode)
    """
    return None

def get_random_file(folder, extensions=[".mp4", ".mov", ".avi", ".mp3", ".wav"]):
    try:
        if not os.path.exists(folder): return None
        files = [f for f in os.listdir(folder) if os.path.splitext(f)[1].lower() in extensions]
        if not files: return None
        return os.path.join(folder, random.choice(files))
    except Exception:
        return None

def process_video(source_video, reaction_video, music_path, voiceover_path, output_path):
    try:
        print(f"\n🎬 VIDEO PROCESSING STARTED (Original Audio Mode)")
        main_video = VideoFileClip(source_video)
        reaction = VideoFileClip(reaction_video)
        
        duration = min(main_video.duration, reaction.duration, Config.MAX_VIDEO_DURATION)
        main_video = main_video.subclip(0, duration)
        reaction = reaction.subclip(0, duration)
        
        main_video = apply_anti_copyright_effects(main_video)
        # main_video = main_video.without_audio() # KEEPING AUDIO
        
        reaction = resize_and_position_video(reaction, Config.CANVAS_WIDTH, Config.REACTION_HEIGHT, 0, "cover")
        main_video = resize_and_position_video(main_video, Config.CANVAS_WIDTH, Config.MAIN_VIDEO_HEIGHT, Config.REACTION_HEIGHT, "contain")
        
        background = ColorClip(size=(Config.CANVAS_WIDTH, Config.CANVAS_HEIGHT), color=(0, 0, 0), duration=duration)
        
        text = random.choice(Config.TEXT_PRESETS["hinglish"])
        text_overlay = create_text_overlay(text, duration)
        
        layers = [background, main_video, reaction]
        if text_overlay: layers.append(text_overlay)
        
        final_video = CompositeVideoClip(layers)
        
        # Audio Mixing: Source + Reaction + Music
        audio_clips = []
        if reaction.audio:
            print("✅ Added Reaction Audio")
            audio_clips.append(reaction.audio)
            
        if main_video.audio:
            print("✅ Added Source Video Audio")
            audio_clips.append(main_video.audio)
        
        if music_path and os.path.exists(music_path):
            music = AudioFileClip(music_path).subclip(0, duration)
            music = music.volumex(Config.MUSIC_VOLUME)
            audio_clips.append(music)
        
        if audio_clips:
            final_video = final_video.set_audio(CompositeAudioClip(audio_clips))
        
        print("💾 Exporting final video...")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        final_video.write_videofile(output_path, fps=30, codec='libx264', audio_codec='aac', preset='medium', threads=4)
        
        main_video.close()
        reaction.close()
        final_video.close()
        
        print(f"\n✅ Video processing completed!")
        return output_path
        
    except Exception as e:
        print(f"❌ Processing error: {str(e)}")
        return None

# ==================== MAIN WORKFLOWS ====================
def create_single_video():
    print("\n📝 VIDEO CREATION WORKFLOW\n")
    video_url = input("Video URL (or Enter for random): ").strip()
    commentary = input("Video Description (For YouTube Title/Desc): ").strip()
    
    if not commentary:
        commentary = "Amazing Reaction Video! Must Watch."
    
    source_video = None
    if video_url:
        download_path = os.path.join(Config.DOWNLOADS_FOLDER, f"source_{datetime.now().strftime('%H%M%S')}.mp4")
        source_video = download_video(video_url, download_path)
    else:
        source_video = get_random_file(Config.DOWNLOADS_FOLDER, [".mp4", ".mov", ".mkv", ".webm"])
    
    if not source_video:
        print("❌ No source video found! Download one first or put in downloads folder.")
        return
    
    reaction_video = get_random_file(Config.REACTIONS_FOLDER, [".mp4", ".mov", ".avi"])
    if not reaction_video:
        print("❌ No reaction video found! Please add to assets/reactions/")
        return
        
    music_file = get_random_file(Config.MUSIC_FOLDER, [".mp3", ".wav"])
    
    # VOICE OVER DISABLED
    voiceover_path = None
    
    output_filename = f"shorts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
    output_path = os.path.join(Config.OUTPUT_FOLDER, output_filename)
    
    result = process_video(source_video, reaction_video, music_file, voiceover_path, output_path)
    
    if result:
        print(f"\n🎉 Video Created: {result}")
        print("\n🚀 AUTO-UPLOADING TO YOUTUBE...")
        title = f"Sentimental Reaction! 😱 #shorts #viral"
        description = f"{commentary}\n\n#shorts #reaction"
        tags = ["shorts", "reaction", "viral"]
        upload_video(result, title, description, tags)

def batch_process():
    print("\n🔄 BATCH PROCESSING MODE\n")
    try:
        num = int(input("How many videos? (1-10): ").strip())
        commentaries = [
            "Wait for the end! 😱",
            "This is so satisfying!",
            "Reaction to viral video",
            "You won't believe this!",
            "Amazing content"
        ]
        
        for i in range(num):
            print(f"\n🎬 Processing Video {i+1}/{num}")
            commentary = random.choice(commentaries)
            
            source_video = get_random_file(Config.DOWNLOADS_FOLDER, [".mp4", ".mov", ".mkv", ".webm"])
            reaction_video = get_random_file(Config.REACTIONS_FOLDER, [".mp4", ".mov", ".avi"])
            music_file = get_random_file(Config.MUSIC_FOLDER, [".mp3", ".wav"])
            
            if not source_video or not reaction_video:
                print("❌ Skipped: Missing assets.")
                continue

            voiceover_path = None # Disabled
            
            output_filename = f"shorts_batch_{i}_{datetime.now().strftime('%H%M%S')}.mp4"
            output_path = os.path.join(Config.OUTPUT_FOLDER, output_filename)
            
            result = process_video(source_video, reaction_video, music_file, voiceover_path, output_path)
            
            if result:
                print("\n🚀 AUTO-UPLOADING TO YOUTUBE...")
                title = f"Amazing Reaction Video {i+1} 😱 #shorts"
                description = f"{commentary}\n\n#shorts #viral"
                tags = ["shorts", "viral", "reaction"]
                upload_video(result, title, description, tags)
                
            print(f"✅ Video {i+1} Done!")
            
    except ValueError:
        print("❌ Invalid number")

import argparse
import sys

# ... Imports ...

# ==================== AUTO MODE (HEADLESS) ====================
def auto_mode():
    """Run autonomously for GitHub Actions"""
    print(f"\n{'='*70}\n🤖 AUTO MODE STARTED\n{'='*70}")
    
    # 1. Search & Download Content
    queries = ["funny cat shorts", "cute dog shorts", "satisfying video", "funny viral clips"]
    query = random.choice(queries)
    print(f"🔍 Searching for: {query}")
    
    search_query = f"ytsearch20:{query}"
    download_path = os.path.join(Config.DOWNLOADS_FOLDER, "auto_video.mp4")
    archive_file = "downloaded_videos.txt"
    
    cmd = [
        "yt-dlp",
        "--match-filter", "duration < 59",
        "-o", download_path,
        "--no-playlist",
        "--max-downloads", "1",
        "--force-overwrites",
        "--download-archive", archive_file,
        search_query
    ]
    subprocess.run(cmd, check=False)
    
    if not os.path.exists(download_path):
        print("❌ Auto-download failed")
        return

    # 2. Get Assets
    reaction_video = get_random_file(Config.REACTIONS_FOLDER, [".mp4", ".mov", ".avi"])
    if not reaction_video:
        print("❌ No reaction videos found! Upload some to assets/reactions/ in your repo.")
        return
        
    music_file = get_random_file(Config.MUSIC_FOLDER, [".mp3", ".wav"])
    if not music_file:
         # Try to download music if missing
         print("🎵 Music missing, downloading default...")
         d = SafeMusicDownloader()
         d.download_music(1, 0)
         music_file = get_random_file(Config.MUSIC_FOLDER, [".mp3", ".wav"])

    # 3. Process
    commentary = "Wait for it! This is amazing. 😱 #shorts"
    output_filename = f"shorts_auto_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
    output_path = os.path.join(Config.OUTPUT_FOLDER, output_filename)
    
    result = process_video(download_path, reaction_video, music_file, None, output_path)
    
    # 4. Upload
    if result:
         print("\n🚀 AUTO-UPLOADING TO YOUTUBE...")
         title = f"Amazing Reaction! 😱 #shorts #viral"
         description = f"{commentary}\n\nSubscribe for more!\n#shorts #reaction #viral"
         tags = ["shorts", "reaction", "viral", "funny"]
         upload_video(result, title, description, tags)
    
    print("\n✅ Auto Mode Finished")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--auto", action="store_true", help="Run in headless auto mode")
    args = parser.parse_args()
    
    create_project_structure()
    
    if args.auto:
        auto_mode()
        return

    print(f"\n{'='*70}\n🎥 YOUTUBE SHORTS FACTORY\n{'='*70}")
    # ... Menu ...
    print("\n1. Download Safe Music")
    print("2. Create Single Video (+ Upload)")
    print("3. Batch Process (+ Upload)")
    
    choice = input("\nChoice (1-3): ").strip()
    
    if choice == "1":
        d = SafeMusicDownloader()
        d.download_music(3, 0)
    elif choice == "2":
        create_single_video()
    elif choice == "3":
        batch_process()
    else:
        print("Exiting...")

if __name__ == "__main__":
    main()
