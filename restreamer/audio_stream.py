import sounddevice as sd


class AudioStream:
    """Class for streaming audio"""

    def __init__(
        self,
        autoplay: bool = False,
        chunk: int = 1024,
        rate: int = 44100,
        input_device: int = 2,
        output_device: int = 4,
    ) -> None:
        self.stopped = autoplay
        self.chunk = chunk
        self.rate = rate
        self.input: sd.InputStream = sd.InputStream(
            device=input_device, samplerate=self.rate, blocksize=self.chunk, channels=1
        )

        self.output: sd.OutputStream = sd.OutputStream(
            device=output_device, samplerate=self.rate, blocksize=self.chunk, channels=1
        )

    def start(self):
        """Start audio loop"""
        self.stopped = False
        self.input.start()
        self.output.start()
        while not self.stopped:
            data, _ = self.input.read(self.chunk)
            self.output.write(data)

    def stop(self):
        """Stop audio loop"""
        self.stopped = True
        self.input.stop()
        self.output.stop()
