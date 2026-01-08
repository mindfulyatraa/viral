"""
Batch processing script for GitHub Actions
"""
from viral_video_bot import ViralVideoBot
import logging
import time
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)

def run_batch():
    print("Starting Batch Process...")
    
    bot = ViralVideoBot()
    
    # Search for viral videos
    logging.info("Searching for viral videos (YouTube/USA)...")
    viral_videos = bot.search_viral_videos_youtube()
    
    if not viral_videos:
        logging.info("No new viral videos found.")
        return
    
    logging.info(f"Found {len(viral_videos)} potential videos")
    
    # Process only ONE video per batch run to avoid timeouts/limits
    # or process all if you prefer
    count = 0
    for video_info in viral_videos:
        if count >= 1: # Limit to 1 video per run for safety
            break
            
        logging.info(f"Processing candidate: {video_info['title']}")
        success = bot.process_viral_video(video_info)
        
        if success:
            count += 1
            logging.info("Video processed and uploaded successfully!")
            
    logging.info(f"Batch complete. Processed {count} videos.")

if __name__ == "__main__":
    run_batch()
