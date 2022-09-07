from tkinter import Tk, Menu, Frame, Label, Toplevel
from threading import Thread
import cv2
from .video_stream import VideoStream


class GUI:
    """Class for the tkinter GUI"""

    def __init__(self) -> None:
        # Main Window
        self.root = Tk()
        self.root.geometry("800x600")

        # Menu Root
        self.menu = Menu(self.root)

        # File Menu
        self.filemenu = Menu(self.menu, tearoff=0)
        self.filemenu.add_command(label="Settings", command=self.settings)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit", command=self.quit)

        self.menu.add_cascade(label="File", menu=self.filemenu)

        # Output Menu
        self.outputmenu = Menu(self.menu, tearoff=0)
        self.outputmenu.add_command(label="Start", command=self.start_video)
        self.outputmenu.add_command(label="Stop", command=self.stop_video)
        self.outputmenu.add_command(label="Raw Output", command=self.raw_video)

        self.menu.add_cascade(label="Output", menu=self.outputmenu)

        self.root.config(menu=self.menu)

        # Display Frame
        self.display = Frame(self.root, bg="white")
        self.display.grid()

        # Embedded video frame
        self.video = Label(self.display)
        self.video.grid()

        # Capture card output
        self.input = VideoStream(src=0, container=self.video)

        self.root.mainloop()

    def start_video(self):
        """Start video output inside tkinter window"""
        self.input.container = self.video
        self.root.geometry(f"{int(self.input.stream.w)}x{int(self.input.stream.h)}")
        Thread(target=self.input.start())

    def stop_video(self):
        """Stop the video output"""
        self.root.geometry("800x600")
        self.video.destroy()
        self.input.stopped = True

    def raw_video(self):
        """Stream the raw output to a cv2 window"""
        self.input.container = None
        Thread(target=self.input.start())

    def quit(self):
        """Exit the program"""
        cv2.destroyAllWindows()
        self.root.destroy()

    def settings(self):
        """Settings window"""
        new_window = Toplevel(self.root)
        new_window.title("Settings")
        new_window.geometry("400x300")
        Label(new_window, text="Test window").pack()
