import sys
import yaml
import pyaudio
import wave
import keyboard
import numpy as np

FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 16000
CHUNK = 512

# Get config details
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)
JOB_DEVICE_MAPPINGS = config["JOB_DEVICE_MAPPINGS"]

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
        streams = [audio.open(format=FORMAT, channels=device["num_channels"], rate=RATE, input=True, input_device_index=device["device_index"], frames_per_buffer=CHUNK) for device in devices]
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

            if keyboard.is_pressed('q'):
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
