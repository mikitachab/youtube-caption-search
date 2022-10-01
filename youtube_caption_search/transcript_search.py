from dataclasses import dataclass, field
from enum import Enum, unique, auto
from typing import List

from youtube_api import (
    YouTubeVideoTranscript,
    YouTubeVideoTranscriptPart,
    YouTubeVideo,
    TranscriptStatus,
)
from helpers import make_watch_url, make_red


@unique
class SearchStatus(Enum):
    INIT = auto()
    NOT_FOUND = auto()
    NO_TRANSCRIPT = auto()
    FOUND = auto()


@dataclass
class SearchResult:
    video_id: str
    video_title: str
    search_str: str
    status: SearchStatus = SearchStatus.INIT
    results: List[YouTubeVideoTranscriptPart] = field(default_factory=list)

    def show(self, color: bool = False):
        print("Video: ", self.video_title)
        for transcript_part in self.results:
            watch_url = make_watch_url(self.video_id, transcript_part["start"])
            text = transcript_part["text"]
            print(text if not color else text.replace(self.search_str, make_red(self.search_str)))
            print(watch_url)
            print()


class TranscriptSearcher:
    def __init__(self, search_str: str, verbose: bool = False):
        self.search_str = search_str
        self.verbose = verbose

    def process_video(self, video: YouTubeVideo) -> SearchResult:
        transcript: YouTubeVideoTranscript = video.transcript
        result = SearchResult(video_id=video.video_id, video_title=video.title, search_str=self.search_str)

        if not transcript or transcript.status == TranscriptStatus.ERROR:
            result.status = SearchStatus.NO_TRANSCRIPT
            if self.verbose:
                print(transcript.error_message)
            return result

        result.results = [
            transcript_part for transcript_part in transcript.data if self.search_str in transcript_part["text"]
        ]

        result.status = SearchStatus.FOUND if len(result.results) > 0 else SearchStatus.NOT_FOUND

        return result
