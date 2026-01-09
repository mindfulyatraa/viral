import yt_dlp
import json

def test_reddit_scrape():
    url = "https://www.reddit.com/r/funny/top/?t=day"
    print(f"Testing yt-dlp scrape for: {url}")
    
    ydl_opts = {
        'extract_flat': True,  # Crucial: Just list videos, don't download
        'playlistend': 5,      # Limit to top 5
        'quiet': True,
        'no_warnings': True,
        # Add headers just in case, though yt-dlp has good defaults
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            print(f"Title: {info.get('title')}")
            print(f"Entry count: {len(info.get('entries', []))}")
            
            for entry in info.get('entries', []):
                print("-" * 20)
                print(f"ID: {entry.get('id')}")
                print(f"Title: {entry.get('title')}")
                print(f"URL: {entry.get('url')}")
                # Check directly what keys we get
                # print(entry.keys())

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_reddit_scrape()
