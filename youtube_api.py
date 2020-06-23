from dataclasses import dataclass
from datetime import datetime
import os
from typing import List, Iterator, Optional

import requests
from youtube_transcript_api import YouTubeTranscriptApi

API_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
DEFAULT_N_VIDEOS = 10
MAX_PAGE_ITEMS = 50


@dataclass
class YouTubeVideo:
    video_id: str
    title: str
    published: datetime
    transcript: List[dict] = None

    @staticmethod
    def from_api_item(item: dict) -> "YouTubeVideo":
        item_snippet = item["snippet"]
        video_id = item_snippet["resourceId"]["videoId"]
        title = item_snippet["title"]
        published = datetime.strptime(item_snippet["publishedAt"], API_DATETIME_FORMAT)
        return YouTubeVideo(video_id, title, published)


class YouTubeApi:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("YT_API_KEY")
        if self.api_key is None:
            raise EnvironmentError("YOUTUBE API key not provided")

    def get_channel_videos(self, channel_id: str, n_videos: int = DEFAULT_N_VIDEOS) -> Iterator[YouTubeVideo]:
        """get list of last n videos of given youtube channel"""
        uploads_id = self._get_uploads_id({"id": channel_id})
        return self._get_videos_by_uploads_id(uploads_id, n_videos)

    def get_user_videos(self, user: str, n_videos: int = DEFAULT_N_VIDEOS) -> Iterator[YouTubeVideo]:
        """get list of last n videos of given youtube channel"""
        uploads_id = self._get_uploads_id({"forUsername": user})
        return self._get_videos_by_uploads_id(uploads_id, n_videos)

    def _get_videos_by_uploads_id(self, uploads_id: str, n_videos: int) -> Iterator[YouTubeVideo]:
        videos_items = self._get_uploads_playlist_items(uploads_id, n_videos)
        videos = (YouTubeVideo.from_api_item(item) for item in videos_items)
        for video in videos:
            video.transcript = YouTubeApi.get_video_transcript(video.video_id)
            yield video

    def _get_uploads_id(self, uploads_owner_param: dict) -> str:
        channels_url = "https://www.googleapis.com/youtube/v3/channels"

        params = {"key": self.api_key, "part": "contentDetails"}
        params.update(uploads_owner_param)

        channels_resp = requests.get(channels_url, params=params)
        uploads_id = channels_resp.json()["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
        return uploads_id

    def _get_uploads_playlist_items(self, uploads_id: str, n_videos: int) -> dict:
        videos_params = {
            "playlistId": uploads_id,
            "key": self.api_key,
            "part": "snippet",
        }
        page_loader = PlaylistPageLoagder(videos_params)
        items = page_loader.load_all_items(n_videos)
        return items

    @staticmethod
    def get_video_transcript(video_id: str) -> Optional[List[dict]]:
        try:
            return YouTubeTranscriptApi.get_transcript(video_id)
        except Exception:  # TODO add specific exception
            return None


class PlaylistPageLoagder:
    PLAYLIST_ITEMS_URL = "https://www.googleapis.com/youtube/v3/playlistItems"

    def __init__(self, init_params):
        self.init_params = init_params

    def _make_playlist_request(self, n_videos: int, page_token: str = None) -> dict:
        params = {**self.init_params, "maxResults": n_videos}
        if page_token is not None:
            params["pageToken"] = page_token
        resp = requests.get(self.PLAYLIST_ITEMS_URL, params=params)
        return resp.json()

    def load_all_items(self, n_videos: int) -> Iterator[dict]:
        page_counts = _make_pages_results_counts(n_videos, MAX_PAGE_ITEMS)
        page_token = None
        for page_count in page_counts:
            page_data = self._make_playlist_request(page_count, page_token)
            page_token = page_data.get("nextPageToken")
            items = page_data.get("items")
            for item in items:
                yield item


def _make_pages_results_counts(n_total: int, n_per_page: int) -> Iterator[int]:
    """make an iterator with numbers maximum n_per_page summing to n_total
        e.g.
        _make_pages_results_counts(150, 50) -> [50, 50, 50]
        _make_pages_results_counts(112, 50) -> [50, 50, 12]
    """
    while n_total:
        if n_total > n_per_page:
            yield n_per_page
            n_total -= n_per_page
        else:
            yield n_total
            n_total = 0
