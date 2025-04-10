
import requests

# API keys
YOUTUBE_API_KEY = "AIzaSyDPzf6aVUsctPVG0JktI72XQNi0Ue3tbMg"

# youtube video fetching
def get_youtube_videos(city):
    search_query = f"Things to do in {city}"
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=3&q={search_query}&key={YOUTUBE_API_KEY}&type=video"
    response = requests.get(url)
    results = response.json()

    videos = []
    for item in results.get("items", []):
        video_id = item["id"]["videoId"]
        title = item["snippet"]["title"]
        thumbnail = item["snippet"]["thumbnails"]["medium"]["url"]
        videos.append({
            "title": title,
            "video_id": video_id,
            "thumbnail": thumbnail
        })
    return videos