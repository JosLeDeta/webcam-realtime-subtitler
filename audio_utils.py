import pyaudio
import numpy as np
import hashlib
import wave, struct

def capture_audio_device(callback, clips_dict, device_index=1, rate=16000, chunk=1024):
    p = pyaudio.PyAudio()
    stream = p.open(
        format = pyaudio.paInt16,
        channels = 1,
        rate = rate,
        input = True,
        frames_per_buffer = chunk,
        input_device_index = device_index
    )

    while True:
        data = stream.read(chunk)
        data = np.frombuffer(data, 'int16')
        callback(data, clips_dict)

def in_silence(data, threshold=2500):
    return np.max(data) < threshold

def generate_silence_samples(data):
    return [0 if in_silence(data) else 100 for n in data]

def get_start_end_points(silent_samples):
    points = []
    point = []
    last = 0
    for i, n in enumerate(silent_samples):
        if last == 0:
            if n != 0 :
                point.append(i)
                last = n
        else:
            if n == 0:
                point.append(i)
                points.append(point)
                point = []
                last = n
    return points

def get_audio_signature(data):
    return hashlib.md5(''.join([str(n) for n in data[-100:]]).encode('utf8')).hexdigest()

def save_wave(filename, data):
    file = wave.open(filename, 'w')
    file.setnchannels(1)
    file.setsampwidth(2)
    file.setframerate(16000)
    for n in data:
        file.writeframesraw(struct.pack('<h', n))

if __name__ == '__main__':
    p = pyaudio.PyAudio()
    device_count = p.get_device_count()
    print('\nInput devices:\n')
    for n in range(device_count):
        info = p.get_device_info_by_index(n)
        device_channels = info["maxInputChannels"]
        if device_channels > 0:
            print(f'[{n}] {info["name"]}')