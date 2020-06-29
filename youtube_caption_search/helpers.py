import argparse


def make_watch_url(video_id: str, start: float) -> str:
    start_at = str(start).split(".")[0]
    return f"https://youtu.be/{video_id}?t={start_at}"


def make_red(str_to_red: str) -> str:
    return f"\033[0;31m{str_to_red}\033[0m"


def get_videos_source_param(args: argparse.Namespace) -> dict:
    if args.user:
        return {"forUsername": args.user}
    if args.channel_id:
        return {"id": args.channel_id}
    raise Exception("videos source not provided")
