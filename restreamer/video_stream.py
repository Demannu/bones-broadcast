from tkinter import Label
from .capture_device import CaptureDevice
from .fps import FPS
import cv2
from PIL import Image, ImageTk


class VideoStream:  # pylint: disable=too-many-arguments
    """Class for streaming capture card output"""

    def __init__(
        self,
        src: int = 0,
        output_fps: int = 60,
        output_w: int = 1920,
        output_h: int = 1080,
        container: Label = None,
    ):
        self.container = container

        # Setup video capture with DirectShow
        self.stream = CaptureDevice(src=src)
        self.stream.set_resolution(output_w, output_h)
        self.stream.set_fps(output_fps)
        self.stream.set_codec()

        # Start FPS counter
        self.fps = FPS()

        # Get first frame to render
        self.grabbed, self.frame = self.stream.cap.read()

        # Ensure we're stopped
        self.stopped = True

    def start(self):
        """Start the capture loop"""
        self.stopped = False
        self.loop()

    def stop(self):
        """Stop the loop"""
        self.frame = []
        self.stopped = True
        cv2.destroyAllWindows()

    def loop(self):
        """Render loop; fetch from device; output to window"""
        if self.stopped:
            return
        (self.grabbed, self.frame) = self.stream.cap.read()
        self.frame = self.fps.render_fps(self.frame)
        # If we weren't given a tkinter label to display in
        if not self.container:
            cv2.imshow("Nintendo Switch", self.frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                self.stop()
            self.fps.update()
            self.loop()
        # If we have a tkinter label to display in
        else:
            # Convert color scheme from BGR to RGBA
            cv2im = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGBA)

            # Render frame in PIL format
            frame = Image.fromarray(cv2im)

            # Render frame in tkinter format
            frametk = ImageTk.PhotoImage(image=frame)

            # Display frame
            self.container.imgtk = frametk
            self.container.configure(image=frametk)

            # Update FPS counter
            self.fps.update()

            self.container.after(1, self.loop)
