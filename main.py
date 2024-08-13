import os
import sys
import yaml
import datetime
import traceback

from src.record import record
from src.transcribe import transcribe
from src.summarize import summarize, summarize_local

# Get config details
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)
RECORDINGS_DIR = config["RECORDINGS_DIR"]
TRANSCRIPTS_DIR = config["TRANSCRIPTS_DIR"]
SUMMARIES_DIR = config["SUMMARIES_DIR"]
JOB_DEVICE_MAPPINGS = config["JOB_DEVICE_MAPPINGS"]
USE_LOCAL_LLAMA = config["USE_LOCAL_LLAMA"]

def main():
    # Get args
    if len(sys.argv) < 3: print("Not enough arguments. Expected 'python main.py <job_index> <meeting_name>'")

    try:
        job_index = int(sys.argv[1])
        meeting = sys.argv[2]

        # Create filepaths using config data
        company = JOB_DEVICE_MAPPINGS[job_index]["company"]
        date = datetime.date.today().strftime('%d-%m-%Y')
        file_prefix = f"{company}_{meeting}_{date}"
        recording_filepath = os.path.join(RECORDINGS_DIR, f"{file_prefix}_recording.wav")
        transcript_filepath = os.path.join(TRANSCRIPTS_DIR, f"{file_prefix}_transcript.txt")
        summary_filepath = os.path.join(SUMMARIES_DIR, f"{file_prefix}_summary.txt")

        # Execute scripts
        print(f"Recording Job {job_index} audio to {recording_filepath}")
        record(job_index, recording_filepath)
        print(f"Transcribing {recording_filepath} to {transcript_filepath}")
        transcribe(recording_filepath, transcript_filepath)
        print(f"Summarizing {transcript_filepath} to {summary_filepath}")
        if USE_LOCAL_LLAMA:
            summarize_local(transcript_filepath, summary_filepath)
        else: 
            summarize(transcript_filepath, summary_filepath)
    except Exception as e:
        print("main.py - Encountered an error, exiting")
        print(f"Exception: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
