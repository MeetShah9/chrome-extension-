from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
from bs4 import BeautifulSoup
import random
from lyricsgenius import Genius

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


# Get Genius token from env or fallback to hardcoded one
GENIUS_TOKEN = os.environ.get("GENIUS_TOKEN") 

genius = Genius(GENIUS_TOKEN, remove_section_headers=True)

genius._session.headers.update({
    "User-Agent": random.choice(USER_AGENTS)
})

@app.route('/')
def health_check():
    return jsonify({"status": "ok", "message": "Lyrics API is running"}), 200

@app.route('/get_lyrics')
def get_lyrics():
    artist = request.args.get("artist")
    track = request.args.get("track")

    if not artist or not track:
        return jsonify({"error": "Missing artist or track name"}), 400

    try:
        song = genius.search_song(track, artist)
        if song and song.lyrics:
            lyrics = song.lyrics.split("Embed")[0].strip()
            return jsonify({ "lyrics": lyrics })
        else:
            return jsonify({ "error": "Lyrics not found." }), 404
    except Exception as e:
        return jsonify({ "error": str(e) }), 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
