import pickle
import base64

try:
    with open('youtube_token.pickle', 'rb') as f:
        data = f.read()
        print(f"Read {len(data)} bytes from pickle")
        encoded = base64.b64encode(data).decode('utf-8')
        
    with open('final_token.txt', 'w', encoding='utf-8') as f:
        f.write(encoded)
    print("Token written to final_token.txt")
except Exception as e:
    print(f"Error: {e}")
