import datetime
import cv2
from collections import deque
from typing import List


class FPS:
    """Class for keeping track of FPS"""

    def __init__(self) -> None:
        self._frames = deque()

    def update(self) -> None:
        """Increase number of frames by 1"""
        now: datetime = datetime.datetime.now()
        while self._frames and (now - self._frames[0]) > datetime.timedelta(seconds=2):
            self._frames.popleft()

        self._frames.append(now)

    def fps(self) -> str:
        """Returns a string representing the current FPS"""
        return str(int(len(self._frames) / 2))

    def render_fps(self, frame) -> List:
        """Adds FPS text to frame"""
        cv2.putText(
            frame,
            self.fps(),
            (4, 16),
            cv2.FONT_HERSHEY_PLAIN,
            1,
            (100, 255, 0),
            1,
            cv2.LINE_AA,
        )
        return frame
