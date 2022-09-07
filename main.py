"""Module for displaying raw MJPG USB input"""
from collections import deque
from threading import Thread
from typing import Dict, List
import cv2
import datetime
from PIL import Image, ImageTk
import pandas as pd
from tkinter import Menu, Tk, Label, Frame
from tkinter import ttk


class GUI:
    def __init__(self) -> None:
        self.root = Tk()
        self.display = Frame(self.root, bg="white")
        self.menu = Menu(self.display)
        self.menu.add_command(label="Start", command=self.start_video)
        self.menu.add_command(label="Stop", command=self.stop_video)
        self.menu.add_command(
            label="Raw Output (press q to quit)", command=self.raw_video
        )
        self.display.grid()
        self.video = Label(self.display)
        self.video.grid()
        self.root.config(menu=self.menu)

        self.root.mainloop()

    def start_video(self):
        self.input = VideoStream(src=0, container=self.video)
        Thread(target=self.input.start())

    def stop_video(self):
        self.input.stopped = True

    def raw_video(self):
        self.input = VideoStream(src=0)
        Thread(target=self.input.start())


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


class VideoStream:
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
        print("starting")
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
        print(self.container)
        # If we weren't given a tkinter label to display in
        if not self.container:
            print("RAW")
            cv2.imshow("Nintendo Switch", self.frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                self.stop()
            self.fps.update()
            self.loop()
        # If we have a tkinter label to display in
        else:
            print("FANCY")
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


class CaptureDevice:
    def __init__(
        self,
        src: int = 0,
        input_fps: int = 60,
        output_w: int = 1920,
        output_h: int = 1080,
    ) -> None:
        self.src = src
        self.cap = cv2.VideoCapture(self.src, cv2.CAP_DSHOW)

        self.input_fps = input_fps
        self.w = output_w
        self.h = output_h

        self.lowest_width = 0
        self.lowest_height = 0
        self.highest_width = 0
        self.highest_height = 0

        self.resolutions = []
        self.aspect_ratio = set()

        # self.get_compatible_resolutions()

    def get_common_resolutions(self):
        url = "https://en.wikipedia.org/wiki/List_of_common_resolutions"
        table = pd.read_html(url)[0]
        table.columns = table.columns.droplevel()
        return table

    def calculate_aspect_ratio(self, w, h):
        def gcd(a, b):
            return a if b == 0 else gcd(b, a % b)

        factor = gcd(w, h)
        x = int(w / factor)
        y = int(h / factor)

        self.aspect_ratio.add(f"{x}:{y}")

    def check_resolution(self, w, h) -> None:
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)

        width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

        if w < width:
            self.lowest_width = width
        if h < height:
            self.lowest_height = height

        if w > width:
            self.highest_width = width
        if h > height:
            self.highest_height = height

        if w == width and h == height:
            self.resolutions.append([w, h])

    def auto_detect(self):
        Thread(target=self.get_compatible_resolutions)

    def get_compatible_resolutions(self):

        common_res = self.get_common_resolutions()
        data = [
            [row["W"], row["H"], row["Display"]]
            for key, row in common_res[["W", "H", "Display"]].iterrows()
        ]

        self.check_resolution(data[0][0], data[0][1])
        self.calculate_aspect_ratio(self.lowest_width, self.lowest_height)

        self.check_resolution(data[-1][0], data[-1][0])
        self.calculate_aspect_ratio(self.highest_width, self.highest_height)

        data = [
            [row[0], row[1]]
            for row in data
            if row[2].replace("∶", ":") in self.aspect_ratio
            and (row[0] >= self.lowest_width and row[0] <= self.highest_width)
            and (row[1] >= self.lowest_height and row[1] <= self.highest_height)
        ]

        for row in data:
            print(f"Checking ({row[0]},{row[1]})")
            self.check_resolution(row[0], row[1])

    def set_resolution(self, w, h):
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)

        self.w = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.h = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

    def set_fps(self, fps: int):
        self.cap.set(cv2.CAP_PROP_FPS, fps)
        self.input_fps = self.cap.get(cv2.CAP_PROP_FPS)

    def set_codec(self):
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc("M", "J", "P", "G"))


# CaptureDevice()
# VideoStream(src=0)
GUI()
cv2.destroyAllWindows()
