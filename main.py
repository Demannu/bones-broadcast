"""Module for displaying raw MJPG USB input"""
from typing import List
import cv2
import datetime


class FPS:
    """Class for keeping track of FPS"""

    def __init__(self) -> None:
        self._start = None
        self._end = None
        self._numFrames = 0

    def start(self) -> "FPS":
        """Set start time to now"""
        self._start = datetime.datetime.now()
        return self

    def stop(self) -> "FPS":
        """Set stop time to now"""
        self._end = datetime.datetime.now()
        return self

    def update(self) -> None:
        """Increase number of frames by 1"""
        self._numFrames += 1

    def fps(self) -> str:
        """Returns a string representing the current FPS"""
        delta_t = (datetime.datetime.now() - self._start).total_seconds()
        if delta_t == 0:
            delta_t = 0.1
        return str(int(self._numFrames / delta_t))

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


class VideoStream:
    """Class for streaming capture card output"""

    def __init__(
        self,
        src: int = 0,
        input_fps: int = 60,
        output_w: int = 1920,
        output_h: int = 1080,
    ):
        self.input_fps = input_fps

        # Setup video capture with DirectShow
        self.stream = cv2.VideoCapture(src, cv2.CAP_DSHOW)

        # Setup video capture settings for Mirabox HD Capture Card
        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, output_w)
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, output_h)
        self.stream.set(cv2.CAP_PROP_FPS, self.input_fps)
        self.stream.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc("M", "J", "P", "G"))

        # Start FPS counter
        self.fps = FPS().start()

        # Get first frame to render
        self.grabbed, self.frame = self.stream.read()

        # Ensure we're running
        self.stopped = False
        self.loop()

    def loop(self):
        """Render loop; fetch from device; output to window"""
        while True:
            if self.stopped:
                return

            (self.grabbed, self.frame) = self.stream.read()
            self.frame = self.fps.render_fps(self.frame)
            cv2.imshow("Nintendo Switch", self.frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                self.stop()
                break
            self.fps.update()

    def stop(self):
        """Stop the FPS timer and loop"""
        self.fps.stop()
        self.stopped = True


# Change src if you have multiple input devices
vs = VideoStream(src=0)

cv2.destroyAllWindows()