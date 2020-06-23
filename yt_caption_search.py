#!/usr/bin/env python3
import argparse
import sys
from typing import List

from youtube_api import YouTubeApi, YouTubeVideo


def main(args):
    channel_id = args.channel_id
    n = args.n_videos
    word = args.word
    user = args.user
    if (user and channel_id) or (not channel_id and not user):
        print("please specify user OR channel id")
        sys.exit(1)
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
    transcript = video.transcript

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
