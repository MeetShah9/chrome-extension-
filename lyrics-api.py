from flask import Flask, request, jsonify
from lyricsgenius import Genius
from flask_cors import CORS

# Setup Flask app
app = Flask(__name__)
CORS(app)

# Genius token
GENIUS_TOKEN = 'U26XhBb1rHkRG6ewM-iUtrbiVrk0FqzORlFkVTkmuBu8SaPmQ7NgqmvfU6DhMuu8'
genius = Genius(GENIUS_TOKEN, remove_section_headers=True)

@app.route('/get_lyrics')
def get_lyrics():
    artist = request.args.get("artist")
    track = request.args.get("track")

    if not artist or not track:
        return jsonify({"error": "Missing artist or track name"}), 400

    try:
        song = genius.search_song(track, artist)
        if song and song.lyrics:
            return jsonify({ "lyrics": song.lyrics })
        else:
            return jsonify({ "error": "Lyrics not found." }), 404
    except Exception as e:
        return jsonify({ "error": str(e) }), 500

if __name__ == '__main__':
    app.run(debug=True)
