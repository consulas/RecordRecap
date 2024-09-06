import os
import sys
import yaml
import datetime
import traceback
import argparse

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
    parser = argparse.ArgumentParser(description='Process jobs')
    parser.add_argument('job_index', type=int, help='Job index')
    parser.add_argument('meeting_name', help='Meeting name')
    parser.add_argument('-s', '--summary-prompt', help='Summary prompt to use', default='meeting')
    args = parser.parse_args()

    try:
        job_index = args.job_index
        meeting = args.meeting_name
        summary_prompt = args.summary_prompt

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
            summarize_local(transcript_filepath, summary_filepath, summary_prompt)
        else: 
            summarize(transcript_filepath, summary_filepath, summary_prompt)
    except Exception as e:
        print("main.py - Encountered an error, exiting")
        print(f"Exception: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
