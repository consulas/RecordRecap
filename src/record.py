import sys
import threading
import yaml
import pyaudio
import wave
import numpy as np
from src.util import get_device_info

FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 16000
CHUNK = 512

class InputThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.daemon = True  # Set the thread as a daemon thread
        self.input = None   # Initialize to store user input

    def run(self):
        while True:
            self.input = input().strip()  # Read user input
            if self.input == 'q':  # Check if 'q' is pressed
                break

# Get config details
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)
JOB_DEVICE_MAPPINGS = config["JOB_DEVICE_MAPPINGS"]

def find_device_index(device_name):
    matching_devices = [device for device in get_device_info() if device["device_name"] == device_name]
    return matching_devices[0].get('device_index')

def record(job_index, filepath):
    try:
        audio = pyaudio.PyAudio()
        devices = JOB_DEVICE_MAPPINGS[job_index]["devices"]
        waveFile = wave.open(filepath, 'wb')
        waveFile.setnchannels(1)  # Only save one channel to waveFile, combine audio streams
        waveFile.setsampwidth(audio.get_sample_size(FORMAT))
        waveFile.setframerate(RATE)

        # Record audio from streams and write to file
        print(f"Press 'q' to stop")
        input_thread = InputThread()
        input_thread.start()
        streams = [audio.open(format=FORMAT, channels=device["num_channels"], rate=RATE, input=True, input_device_index=find_device_index(device["device_name"]), frames_per_buffer=CHUNK) for device in devices]
        while True:
            channel_audios = []
            for stream, device in zip(streams, devices):
                raw_audio = np.frombuffer(stream.read(CHUNK), dtype=np.int16)
                # Ex: For 2 channels, audio is interleaved [L0, R0, L1, R1, L2, R2, ...]. 
                # Use channel as start and num_channels as step to get all values from one channel
                channel_audio = raw_audio[device["channel"]::device["num_channels"]]
                channel_audios.append(channel_audio)
            
            # Sum channel_audios
            if channel_audios:
                mixed_audio = np.sum(channel_audios, axis = 0)
                waveFile.writeframes(mixed_audio.astype(np.int16).tobytes())

            if input_thread.input == 'q':  # Check input from the input thread
                print("Quitting...")
                break

    except Exception as e:
        print(f"record.py - An error occured during recording")
        raise
    else:
        print(f"Recorded Job {job_index} audio to {filepath}")
    finally:
        for stream in streams:
            stream.stop_stream()
            stream.close()
        waveFile.close()
        audio.terminate()

if __name__ == "__main__":
    if len(sys.argv) < 3: print("Not enough arguments. Expected 'python record.py <job_index> <filename>'")
    record(int(sys.argv[1]), sys.argv[2])
