import sys
import yaml
import whisper

# Get config details
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)
WHISPER_MODEL = config["WHISPER_MODEL"]
LANGUAGE = "en"

def transcribe(recording_filepath, transcript_filepath):
    try:
        # Load model and transcribe
        model = whisper.load_model(WHISPER_MODEL)
        result = model.transcribe(recording_filepath, temperature=0.0)
        transcript = result["text"]

        # Save the transcript
        with open(transcript_filepath, 'w') as f:
            f.write(transcript)
    except Exception as e:
        print(f"transcribe.py - An error occured during transcription")
        raise
    else: 
        return transcript

if __name__ == "__main__":
    if len(sys.argv) < 3: print("Not enough arguments. Expected 'python transcribe.py <recording_filepath> <transcript_filepath>'")
    transcribe(sys.argv[1], sys.argv[2])