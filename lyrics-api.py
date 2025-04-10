from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
from bs4 import BeautifulSoup
import random

# Setup Flask app
app = Flask(__name__)
CORS(app)

# Rotate user agents to avoid being blocked
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1"
]

@app.route('/get_lyrics')
def get_lyrics():
    artist = request.args.get("artist")
    track = request.args.get("track")
    
    if not artist or not track:
        return jsonify({"error": "Missing artist or track name"}), 400
    
    # Use direct scraping approach instead of the Genius library
    try:
        # Step 1: Search for the song
        query = f"{track} {artist} lyrics"
        search_url = f"https://www.google.com/search?q={requests.utils.quote(query)}"
        
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.google.com/",
            "Cache-Control": "no-cache"
        }
        
        # Try to find the Genius page via Google
        search_res = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(search_res.text, "html.parser")
        
        # Look for Genius links in Google results
        genius_link = None
        for link in soup.find_all('a'):
            href = link.get('href')
            if href and 'genius.com' in href and '/lyrics/' in href:
                genius_link = href
                # Extract the real URL from Google's redirect
                if '/url?q=' in genius_link:
                    genius_link = genius_link.split('/url?q=')[1].split('&')[0]
                break
        
        if not genius_link:
            return jsonify({"error": "Could not find lyrics page"}), 404
            
        # Step 2: Get the lyrics page
        song_page = requests.get(genius_link, headers={
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml",
            "Referer": search_url
        }, timeout=10)
        
        song_soup = BeautifulSoup(song_page.text, "html.parser")
        
        # Find the lyrics content
        lyrics_divs = song_soup.find_all("div", attrs={"data-lyrics-container": "true"})
        
        if not lyrics_divs:
            return jsonify({"error": "Lyrics container not found on page"}), 404
        
        # Combine all the lyrics sections
        lyrics = ""
        for div in lyrics_divs:
            section_text = div.get_text("\n")
            lyrics += section_text + "\n\n"
        
        return jsonify({"lyrics": lyrics.strip()})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def health_check():
    return jsonify({"status": "ok", "message": "Lyrics API is running"}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
