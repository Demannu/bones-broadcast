# Stripped Down Streamer
This does the absolute bare minimum, it displays a video feed from a USB device.

Solutions like OBS and Streamlabs have *nearly* no lag, but it's noticable through my Mirabox HD Capture Card.

I wanted a way to get no-latency or as close to that as possible with just a video stream and python.

## Notes
* If you only have 1 USB input device, the input `src` will be 0.
* If you have multiple inputs, increase the `src` by 1 until you find the one you want
* Press `Q` to exit the stream, the X will not close the program.

