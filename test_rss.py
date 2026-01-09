import requests
import xml.etree.ElementTree as ET

def test_rss():
    subreddit = "funny"
    url = f"https://www.reddit.com/r/{subreddit}/top/.rss?t=day&limit=10"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    print(f"Testing RSS feed: {url}")
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("Content received (first 500 chars):")
            print(response.text[:500])
            
            # Simple parsing check
            root = ET.fromstring(response.text)
            # RSS 2.0 uses 'channel' -> 'item', Atom uses 'entry'
            # Reddit usually returns Atom
            
            # Print namespace if any
            print(f"Root tag: {root.tag}")
            
            # Iterating entries (Atom format usually)
            count = 0
            for child in root:
                if 'entry' in child.tag:
                    count += 1
                    title = child.find('{http://www.w3.org/2005/Atom}title').text
                    link = child.find('{http://www.w3.org/2005/Atom}link').attrib['href']
                    print(f"\nEntry {count}:")
                    print(f"Title: {title}")
                    print(f"Link: {link}")
                    
            print(f"\nFound {count} entries.")
            
        else:
            print("Failed to fetch RSS feed.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_rss()
