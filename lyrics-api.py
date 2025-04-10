# from flask import Flask, request, jsonify
# from lyricsgenius import Genius
# from flask_cors import CORS
# import os
# # Setup Flask app
# app = Flask(__name__)
# CORS(app)




# # Genius token
# GENIUS_TOKEN = 'U26XhBb1rHkRG6ewM-iUtrbiVrk0FqzORlFkVTkmuBu8SaPmQ7NgqmvfU6DhMuu8'
# genius = Genius(GENIUS_TOKEN, remove_section_headers=True)

# # 👇 Inject a browser-like User-Agent to avoid 403
# genius._session.headers.update({
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/115.0 Safari/537.36"
# })



# @app.route('/get_lyrics')
# def get_lyrics():
#     artist = request.args.get("artist")
#     track = request.args.get("track")

#     if not artist or not track:
#         return jsonify({"error": "Missing artist or track name"}), 400

#     try:
#         song = genius.search_song(track, artist)
#         if song and song.lyrics:
#             return jsonify({ "lyrics": song.lyrics })
#         else:
#             return jsonify({ "error": "Lyrics not found." }), 404
#     except Exception as e:
#         return jsonify({ "error": str(e) }), 500

# if __name__ == '__main__':
#     # When running in a deployment environment, use the PORT environment variable
#     # and bind to 0.0.0.0 to allow external connections
#     port = int(os.environ.get("PORT", 5000))
#     app.run(host='0.0.0.0', port=port, debug=False)



# workourd method:


import requests
from bs4 import BeautifulSoup
app = Flask(__name__)
CORS(app)


@app.route('/get_lyrics')
def get_lyrics():
    artist = request.args.get("artist")
    track = request.args.get("track")

    if not artist or not track:
        return jsonify({ "error": "Missing artist or track name" }), 400

    query = f"{track} {artist}"
    search_url = f"https://genius.com/api/search/multi?q={requests.utils.quote(query)}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/115.0 Safari/537.36"
    }

    try:
        search_res = requests.get(search_url, headers=headers)
        search_data = search_res.json()

        hits = search_data["response"]["sections"][0]["hits"]
        if not hits:
            return jsonify({ "error": "No results found." }), 404

        song_url = hits[0]["result"]["url"]

        # Now fetch the song page
        song_page = requests.get(song_url, headers=headers)
        soup = BeautifulSoup(song_page.text, "html.parser")
        lyrics_div = soup.find("div", {"data-lyrics-container": "true"})

        if not lyrics_div:
            return jsonify({ "error": "Lyrics not found on page." }), 404

        lyrics = "\n".join([tag.get_text() for tag in lyrics_div.find_all("p")])
        return jsonify({ "lyrics": lyrics })

    except Exception as e:
        return jsonify({ "error": str(e) }), 500

