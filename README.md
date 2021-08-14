# webcam-realtime-subtitler

An attempt to make a webcam subtitler using PyAudio and [Silero Speech-To-Text PyTorch model](https://github.com/snakers4/silero-models).

It uses pyvirtualcam to relay webcam input to virtual webcam device and adds the subtitles to it

## Usage

```shell

usage: main.py [-h] [--lang LANG] [--video-device VIDEO_DEVICE]
               [--audio-device AUDIO_DEVICE]

optional arguments:
  -h, --help            show this help message and exit
  --lang LANG           en, es, de
  --video-device VIDEO_DEVICE
                        input video device index
  --audio-device AUDIO_DEVICE
                        input audio device index
```