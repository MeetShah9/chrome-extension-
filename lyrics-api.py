from flask import Flask, request, jsonify
from lyricsgenius import Genius
from flask_cors import CORS
import os
import random

# Setup Flask app
app = Flask(__name__)
CORS(app)

# Genius token
GENIUS_TOKEN = 'U26XhBb1rHkRG6ewM-iUtrbiVrk0FqzORlFkVTkmuBu8SaPmQ7NgqmvfU6DhMuu8'

# Create a Genius client with better headers
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0"
]

genius = Genius(GENIUS_TOKEN, remove_section_headers=True)

# Configure the session with better headers
genius._session.headers.update({
    "User-Agent": random.choice(USER_AGENTS),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Cache-Control": "max-age=0"
})

@app.route('/get_lyrics')
def get_lyrics():
    artist = request.args.get("artist")
    track = request.args.get("track")
    
    if not artist or not track:
        return jsonify({"error": "Missing artist or track name"}), 400
    
    try:
        song = genius.search_song(track, artist)
        if song and song.lyrics:
            # Clean up the lyrics (remove trailing Genius text)
            lyrics = song.lyrics
            if "Embed" in lyrics:
                lyrics = lyrics.split("Embed")[0]
            
            return jsonify({"lyrics": lyrics})
        else:
            return jsonify({"error": "Lyrics not found."}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def health_check():
    return jsonify({"status": "ok", "message": "Lyrics API is running"}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
