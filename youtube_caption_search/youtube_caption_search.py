#!/usr/bin/env python3
import argparse
import sys

from .youtube_api import YouTubeApi
from .transcript_search import TranscriptSearcher


def main():
    parser = argparse_setup()
    args = parser.parse_args()
    channel_id = args.channel_id
    n_videos = args.n_videos
    word = args.word
    user = args.user

    if (user and channel_id) or (not channel_id and not user):
        print("please specify user OR channel id")
        sys.exit(1)

    yt_api = YouTubeApi()
    if channel_id:
        videos = yt_api.get_channel_videos(channel_id, n_videos)
    else:
        videos = yt_api.get_user_videos(user, n_videos)

    searcher = TranscriptSearcher(word)
    for index, video in enumerate(videos, 1):
        print(f"{index}. ", end="")
        result = searcher.process_video(video)
        print(result)


def argparse_setup():
    parser = argparse.ArgumentParser("yt_caption_search.py", description="search for word in youtube videos")
    parser.add_argument("--word", "-w", type=str, help="word to search", required=True)
    parser.add_argument("--channel-id", "-c", type=str, help="channel_id to search from")
    parser.add_argument("--user", "-u", type=str, help="user to search from")
    parser.add_argument(
        "--n-videos", "-n", type=int, help="n last vides to search in channel", default=5,
    )
    return parser


def make_watch_url(video_id: str, start: float) -> str:
    start_at = str(start).split(".")[0]
    return f"https://youtu.be/{video_id}?t={start_at}"


def make_red(str_to_red: str) -> str:
    return f"\033[0;31m{str_to_red}\033[0m"


def print_found_result(found_word: str, transcript_part: dict, video_id: str, color=True):
    watch_url = make_watch_url(video_id, transcript_part["start"])
    text = transcript_part["text"]
    if color:
        print(text.replace(found_word, make_red(found_word)))
    else:
        print(text)
    print(watch_url)
    print()
