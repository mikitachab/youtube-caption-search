import argparse
from dataclasses import dataclass
import sys
import os
from typing import List

import requests
from youtube_transcript_api import YouTubeTranscriptApi


def main(args):
    channel_id = args.channel_id
    n = args.n_videos
    word = args.word
    user = args.user
    if (user and channel_id) or (not channel_id and not user):
        print("please specify user OR channel id")
        exit(1)
    yt_api = YouTubeApi()
    if channel_id:
        videos = yt_api.get_channel_videos(channel_id, n)
    else:
        videos = yt_api.get_user_videos(user, n)
    for index, video in enumerate(videos, 1):
        print(f"{index}. ", end="")
        search_video_transcript(video, word)


def argparse_setup():
    parser = argparse.ArgumentParser("yt_caption_search.py", description="search for word in youtube videos")
    parser.add_argument("--word", "-w", type=str, help="word to search", required=True)
    parser.add_argument("--channel-id", "-c", type=str, help="channel_id to search from")
    parser.add_argument("--user", "-u", type=str, help="user to search from")
    parser.add_argument(
        "--n-videos", "-n", type=int, help="n last vides to search in channel", default=5,
    )
    return parser


@dataclass
class YouTubeVideo:
    video_id: str
    title: str

    @staticmethod
    def from_api_item(item: dict) -> "YouTubeVideo":
        video_id = item["snippet"]["resourceId"]["videoId"]
        title = item["snippet"]["title"]
        return YouTubeVideo(video_id, title)


class YouTubeApi:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("YT_API_KEY")

    def get_channel_videos(self, channel_id: str = None, n: int = 5) -> List[YouTubeVideo]:
        """get list of last n videos of given youtube channel"""
        uploads_id = self._get_uploads_id({"id": channel_id})
        return self._get_videos_by_uploads_id(uploads_id, n)

    def get_user_videos(self, user: str, n: int = 5) -> List[YouTubeVideo]:
        """get list of last n videos of given youtube channel"""
        uploads_id = self._get_uploads_id({"forUsername": user})
        return self._get_videos_by_uploads_id(uploads_id, n)

    def _get_videos_by_uploads_id(self, uploads_id: str, n: int) -> List[YouTubeVideo]:
        videos_data = self._get_uploads_playlist_data(uploads_id, n)
        videos = [YouTubeVideo.from_api_item(item) for item in videos_data["items"]]
        return videos

    def _get_uploads_id(self, uploads_owner_param: dict) -> str:
        channels_url = "https://www.googleapis.com/youtube/v3/channels"

        params = {"key": self.api_key, "part": "contentDetails"}
        params.update(uploads_owner_param)

        channels_resp = requests.get(channels_url, params=params)
        uploads_id = channels_resp.json()["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
        return uploads_id

    def _get_uploads_playlist_data(self, uploads_id: str, n: int) -> dict:
        videos_url = "https://www.googleapis.com/youtube/v3/playlistItems"

        videos_params = {
            "playlistId": uploads_id,
            "key": self.api_key,
            "part": "snippet",
            "maxResults": n,
        }

        videos_resp = requests.get(videos_url, params=videos_params)
        return videos_resp.json()


def get_video_transcript(video_id: str) -> List[dict]:
    try:
        return YouTubeTranscriptApi.get_transcript(video_id)
    except Exception:
        print("Cant fetch subtitles for this video")
        return None


def make_watch_url(video_id: str, start: float) -> str:
    start_at = str(start).split(".")[0]
    return f"https://youtu.be/{video_id}?t={start_at}"


def make_red(str_to_red: str) -> str:
    return f"\033[0;31m{str_to_red}\033[0m"


def transcript_search(transcript: List[dict], search_str):
    for transcript_part in transcript:
        text = transcript_part["text"]
        if search_str in text:
            print(text.replace(search_str, make_red(search_str)))


def print_found_result(found_word: str, transcript_part: dict, video_id: str, color=True):
    watch_url = make_watch_url(video_id, transcript_part["start"])
    text = transcript_part["text"]
    if color:
        print(text.replace(found_word, make_red(found_word)))
    else:
        print(text)
    print(watch_url)
    print()


def search_video_transcript(video: YouTubeVideo, search_str: str, color=True):
    print(f"Searching video: {video.title}")
    video_id = video.video_id

    transcript = get_video_transcript(video_id)
    if not transcript:
        return

    for transcript_part in transcript:
        text = transcript_part["text"]
        if search_str in text:
            print_found_result(search_str, transcript_part, video_id, color)


if __name__ == "__main__":
    parser = argparse_setup()
    args = parser.parse_args()
    sys.exit(main(args))
