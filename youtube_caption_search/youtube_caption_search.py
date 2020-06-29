#!/usr/bin/env python3
import argparse
import os

from .youtube_api import YouTubeApi
from .transcript_search import (
    TranscriptSearcher,
    SearchResult,
    SearchStatus,
)
from .helpers import get_videos_source_param


def main():
    parser = argparse_setup()
    args = parser.parse_args()
    word = args.word
    color = not args.no_color
    api_key = args.api_key or os.getenv("YOUTUBE_API_KEY")
    source_param: dict = get_videos_source_param(args)

    if api_key is None:
        parser.error("YOUTUBE API key is not provided")

    yt_api = YouTubeApi(api_key)
    videos = yt_api.get_videos(source_param, args.n_videos)
    searcher = TranscriptSearcher(word, verbose=args.verbose)
    for video in videos:
        result: SearchResult = searcher.process_video(video)
        if result.status == SearchStatus.FOUND:
            result.show(color=color)


def argparse_setup():
    parser = argparse.ArgumentParser("yt_caption_search.py", description="search for word in youtube videos")

    videos_source_group = parser.add_mutually_exclusive_group()
    videos_source_group.add_argument("--channel-id", "-c", type=str, help="channel_id to search from")
    videos_source_group.add_argument("--user", "-u", type=str, help="user to search from")

    parser.add_argument("--word", "-w", type=str, help="word to search", required=True)
    parser.add_argument(
        "--n-videos", "-n", type=int, help="n last vides to search in channel", default=5,
    )
    parser.add_argument("--api-key", "-k", type=str, help="YouTube Data API key", default=None)
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument("--no-color", action="store_true")

    return parser
