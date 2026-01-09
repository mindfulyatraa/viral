import requests

def test_access():
    url = "https://v.redd.it/90dfett5j3cg1" # Example from log
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Referer': 'https://www.reddit.com/'
    }
    
    print(f"Testing access to {url}")
    try:
        response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        print(f"Status Code: {response.status_code}")
        print(f"Final URL: {response.url}")
        print(f"Headers: {response.headers}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_access()
