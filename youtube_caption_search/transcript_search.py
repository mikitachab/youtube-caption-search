from dataclasses import dataclass
from enum import Enum, unique, auto
from typing import List

from .youtube_api import YouTubeVideoTranscript, YouTubeVideoTranscriptPart, YouTubeVideo


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
    results: List[YouTubeVideoTranscriptPart] = None


class TranscriptSearcher:
    def __init__(self, search_str: str):
        self.search_str = search_str

    def process_video(self, video: YouTubeVideo):
        transcript: YouTubeVideoTranscript = video.transcript
        result = SearchResult(video_id=video.video_id, video_title=video.title, search_str=self.search_str)

        if not transcript:
            result.status = SearchStatus.NO_TRANSCRIPT
            return result

        result.results = [
            transcript_part for transcript_part in transcript if self.search_str in transcript_part["text"]
        ]

        result.status = SearchStatus.FOUND if len(result.results) > 0 else SearchStatus.NOT_FOUND

        return result
