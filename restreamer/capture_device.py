import cv2
from threading import Thread


class CaptureDevice:  # pylint: disable=too-many-instance-attributes, invalid-name
    """Class for the capture interface"""

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

    def get_common_resolutions(self):
        """Fetch list of common resolutions from wikipedia"""
        url = "https://en.wikipedia.org/wiki/List_of_common_resolutions"
        table = pd.read_html(url)[0]
        table.columns = table.columns.droplevel()
        return table

    def calculate_aspect_ratio(self, w, h):
        """Calculate and add aspect ratio to class"""

        def gcd(a, b):
            return a if b == 0 else gcd(b, a % b)

        factor = gcd(w, h)
        x = int(w / factor)
        y = int(h / factor)

        self.aspect_ratio.add(f"{x}:{y}")

    def check_resolution(self, w, h) -> None:
        """Check to see if provided resolution is compatible with device"""
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
        """Run the resolution detection function in a thread"""
        Thread(target=self.get_compatible_resolutions)

    def get_compatible_resolutions(self):
        """Return a list of compatible resolutions"""

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
            self.check_resolution(row[0], row[1])

    def set_resolution(self, w, h):
        """Set resolution of the capture device"""
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)

        self.w = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.h = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

    def set_fps(self, fps: int):
        """Set FPS of the capture device"""
        self.cap.set(cv2.CAP_PROP_FPS, fps)
        self.input_fps = self.cap.get(cv2.CAP_PROP_FPS)

    def set_codec(self):
        """Set the codec of the capture device"""
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc("M", "J", "P", "G"))
