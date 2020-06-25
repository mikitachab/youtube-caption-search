#!/usr/bin/env python3
import argparse
import sys
import os

from .youtube_api import YouTubeApi
from .transcript_search import (
    TranscriptSearcher,
    SearchResult,
    SearchStatus,
)


def main():
    parser = argparse_setup()
    args = parser.parse_args()
    channel_id = args.channel_id
    n_videos = args.n_videos
    word = args.word
    user = args.user
    verbose = args.verbose
    api_key = args.api_key or os.getenv("YOUTUBE_API_KEY")

    if api_key is None:
        raise EnvironmentError("YOUTUBE API key is not provided")

    if (user and channel_id) or (not channel_id and not user):
        print("please specify user OR channel id")
        sys.exit(1)

    yt_api = YouTubeApi(api_key)
    if channel_id:
        videos = yt_api.get_channel_videos(channel_id, n_videos)
    else:
        videos = yt_api.get_user_videos(user, n_videos)

    searcher = TranscriptSearcher(word, verbose=verbose)
    for video in videos:
        result: SearchResult = searcher.process_video(video)
        if result.status == SearchStatus.FOUND:
            result.show(color=True)


def argparse_setup():
    parser = argparse.ArgumentParser("yt_caption_search.py", description="search for word in youtube videos")
    parser.add_argument("--word", "-w", type=str, help="word to search", required=True)
    parser.add_argument("--channel-id", "-c", type=str, help="channel_id to search from")
    parser.add_argument("--user", "-u", type=str, help="user to search from")
    parser.add_argument(
        "--n-videos", "-n", type=int, help="n last vides to search in channel", default=5,
    )
    parser.add_argument("--api-key", "-k", type=str, help="YouTube Data API key", default=None)
    parser.add_argument("--verbose", "-v", action="store_true", default=False)
    return parser
