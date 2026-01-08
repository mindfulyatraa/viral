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
    
    # Debug: Check reaction videos
    logging.info(f"Checking reaction directory: {bot.config.get('reaction_dir')}")
    if os.path.exists(bot.config.get('reaction_dir')):
        files = os.listdir(bot.config.get('reaction_dir'))
        logging.info(f"Files in reaction dir: {files}")
    else:
        logging.error("Reaction directory does not exist!")

    # Search for viral videos
    logging.info("Searching for viral videos (YouTube/USA)...")
    viral_videos = bot.search_viral_videos_youtube()
    
    if not viral_videos:
        logging.error("No new viral videos found.")
        sys.exit(1) # Force fail
    
    logging.info(f"Found {len(viral_videos)} potential videos")
    
    # Process
    count = 0
    for video_info in viral_videos:
        if count >= 1: 
            break
            
        logging.info(f"Processing candidate: {video_info['title']}")
        success = bot.process_viral_video(video_info)
        
        if success:
            count += 1
            logging.info("Video processed and uploaded successfully!")
        else:
            logging.error(f"Failed to process video: {video_info['title']}")
            
    logging.info(f"Batch complete. Processed {count} videos.")
    
    if count == 0:
        logging.error("Batch finished with 0 processed videos.")
        sys.exit(1) # Force fail if nothing happened()

if __name__ == "__main__":
    run_batch()
