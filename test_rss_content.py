import requests
import xml.etree.ElementTree as ET

def test_rss_content():
    subreddit = "funny"
    url = f"https://www.reddit.com/r/{subreddit}/top/.rss?t=day&limit=5"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/xml,application/atom+xml,text/html,*/*;q=0.9'
    }
    
    print(f"Fetching RSS: {url}")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            root = ET.fromstring(response.text)
            namespace = {'atom': 'http://www.w3.org/2005/Atom'}
            
            entries = root.findall('atom:entry', namespace)
            if not entries:
                entries = root.findall('{http://www.w3.org/2005/Atom}entry')
                
            print(f"Found {len(entries)} entries. Checking for content...")
            
            for i, entry in enumerate(entries):
                content = entry.find('atom:content', namespace)
                if content is None:
                    content = entry.find('{http://www.w3.org/2005/Atom}content')
                
                content_html = content.text if content is not None else "No content"
                
                print(f"\nEntry {i+1} Content Preview:")
                print(content_html[:500]) # First 500 chars
                
                if "v.redd.it" in content_html:
                    print(">>> FOUND v.redd.it LINK IN CONTENT! <<<")
                else:
                    print("No v.redd.it link found.")
                    
        else:
            print(f"Failed: {response.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_rss_content()
