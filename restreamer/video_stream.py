import cv2

from .capture_device import CaptureDevice
from .fps import FPS


class VideoStream:  # pylint: disable=too-many-arguments
    """Class for streaming capture card output"""

    def __init__(
        self,
        src: int = 0,
        device_name: str = "USB Input",
        output_fps: int = 60,
        output_w: int = 1920,
        output_h: int = 1080,
    ):

        self.device_name = device_name

        # Setup video capture with DirectShow
        self.stream = CaptureDevice(src=src)
        self.output_w = output_w
        self.output_h = output_h
        self.output_fps = output_fps
        self.setup()

        # Start FPS counter
        self.fps = FPS()

        # Get first frame to render
        self.grabbed, self.frame = self.stream.cap.read()

        # Ensure we're stopped
        self.stopped = True

    def start(self):
        """Start the capture loop"""
        self.stopped = False
        print(self.frame)
        self.loop()

    def stop(self):
        """Stop the loop"""
        self.frame = []
        self.stopped = True
        cv2.destroyAllWindows()

    def setup(self):
        self.stream.set_resolution(self.output_w, self.output_h)
        self.stream.set_fps(self.output_fps)
        self.stream.set_codec()

    def set_resolution(self, resolution):
        w, h = resolution.widget.get().split(" x ")
        self.output_w = int(w)
        self.output_h = int(h)
        self.stream = CaptureDevice(
            self.src, self.output_fps, self.output_w, self.output_h
        )
        self.setup()

    def set_device(self, video_src):
        video_src.widget.get()
        self.src = video_src.widget.current()
        self.stream = CaptureDevice(self.src)
        self.setup()
        self.grabbed, self.frame = self.stream.cap.read()

    def hard_stop(self, msg):
        print(f"[HARD STOP] {msg}")

    def loop(self):
        """Render loop; fetch from device; output to window"""
        while not self.stopped:
            (self.grabbed, self.frame) = self.stream.cap.read()
            self.frame = self.fps.render_fps(self.frame)
            cv2.imshow(self.device_name, self.frame)

            if (cv2.waitKey(1) & 0xFF == ord("q")) or cv2.getWindowProperty(
                self.device_name, cv2.WND_PROP_VISIBLE
            ) < 1:
                self.stop()
            self.fps.update()
