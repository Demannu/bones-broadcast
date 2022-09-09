from tkinter import TOP, StringVar, Tk, Menu, Frame, Label, Toplevel
from threading import Thread
from tkinter.ttk import Button, Combobox
import cv2
from .video_stream import VideoStream
from .audio_stream import AudioStream


class GUI:
    """Class for the tkinter GUI"""

    def __init__(self) -> None:
        # Main Window
        self.root = Tk()
        # self.root.geometry("400x300")

        # Menu Root
        self.menu = Menu(self.root)

        # File Menu
        self.filemenu = Menu(self.menu, tearoff=0)
        self.filemenu.add_command(label="Exit", command=self.quit)

        self.menu.add_cascade(label="File", menu=self.filemenu)

        # Output Menu
        self.outputmenu = Menu(self.menu, tearoff=0)
        self.outputmenu.add_command(label="Raw Output", command=self.raw_video)

        self.menu.add_cascade(label="Output", menu=self.outputmenu)

        self.root.config(menu=self.menu)

        # Display Frame
        self.display = Frame(self.root, bg="white")
        self.display.grid()

        # Video Input Device Configuration
        video_input_devices = ["Run auto detect"]
        vid_variable = StringVar(self.display)

        vid_combobox = Combobox(self.display, values=video_input_devices).pack()

        # Video Resolution Configuration
        video_resolutions = []
        vr_variable = StringVar(self.display)

        vr_combobox = Combobox(self.display, values=video_resolutions).pack()

        # Auto-detect: Input resolution
        auto_video_resolution = Button(
            self.display,
            text="Auto Detect Resolutions",
            command=self.auto_detect_video_resolutions,
        ).pack()

        # Capture card output
        self.video_input = VideoStream(src=0)
        self.audio_input = AudioStream(input_device=2, output_device=4)

        self.video_thread = None
        self.audio_thread = None

        self.root.mainloop()

    def auto_detect_video_resolutions(self):
        pass

    def raw_video(self):
        """Stream the raw output to a cv2 window"""
        self.display.master.withdraw()
        self.audio_thread: Thread = Thread(target=self.audio_input.start).start()
        self.video_thread: Thread = Thread(target=self.video_input.start).start()
        while not self.video_input.stopped:
            continue
        self.display.master.deiconify()
        self.stop()

    def stop(self):
        self.audio_input.stop()
        self.video_input.stop()
        if self.video_thread and self.audio_thread:
            self.video_thread.join()
            self.audio_thread.join()

    def quit(self):
        """Exit the program"""
        cv2.destroyAllWindows()
        self.stop()
        self.root.destroy()
