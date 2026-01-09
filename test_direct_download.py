
import logging
import os
import sys
from viral_video_bot import ViralVideoBot

# Configure logging
logging.basicConfig(level=logging.INFO)

def test_direct_download():
    bot = ViralVideoBot('config.json')
    
    # Test case: A known viral video from Reddit (or one found via RSS)
    # We'll mock the video_info as if it came from the new search method
    
    # You might need to find a fresh active link or just use a known one if available.
    # Since I don't have a live fresh URL guarantee, I will try to fetch one using the bot's own search first.
    
    print("Searching for a video to test...")
    videos = bot.search_viral_videos_reddit()
    
    if not videos:
        print("No videos found in RSS. Cannot test download.")
        return

    target_video = videos[0]
    print(f"Testing download for: {target_video['title']}")
    print(f"Direct URL: {target_video.get('direct_url')}")
    
    output_path = "test_download.mp4"
    if os.path.exists(output_path):
        os.remove(output_path)
        
    result = bot.download_video(target_video, output_path)
    
    if result:
        print(f"SUCCESS: Video downloaded to {output_path}")
        print(f"File size: {os.path.getsize(output_path) / 1024 / 1024:.2f} MB")
    else:
        print("FAILURE: Download failed.")

if __name__ == "__main__":
    test_direct_download()
