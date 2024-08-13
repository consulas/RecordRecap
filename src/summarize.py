import sys
import yaml 
import subprocess
import requests
import time

# Get config details
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

LLAMA_SERVER = config["LLAMA_SERVER"]
LLAMA_MODEL = config["LLAMA_MODEL"]
LLAMA_CONTEXT = config["LLAMA_CONTEXT"]
LLAMA_PORT = config["LLAMA_PORT"]
OPENAI_ENDPOINT = config["OPENAI_ENDPOINT"]
OPENAI_API_KEY = config["OPENAI_API_KEY"]

# Using llama-server.exe to provide an OpenAI API endpoint. 
# Allows people with no local GPU to use other APIs
def summarize(transcript_filepath, summary_filepath):
    with open(transcript_filepath, 'r', encoding='utf-8') as f:
        transcript = f.read()

    # TODO Abstract to use OpenAI API python library?
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You are a senior software engineer and product manager."},
            {"role": "user", "content":
            f"""
            Summarize the following meeting transcript. Give me brief 1 paragraph Summary, key Action Items, and a meeting Outline using the following format.\n
            Format:\n
            # Summary\n
            <insert summary here>\n
            # Action Items\n
            - <insert action item>\n
            # Outline\n
            - <insert outline item>\n
            Transcript:\n
            {transcript}
            """}
           ],
        "temperature": 0.7
    }

    response = requests.post(OPENAI_ENDPOINT, headers=headers, json=data)
    if response.status_code == 200:
        summary = response.json()["choices"][0]["message"]["content"]
        print(summary)
        # Save the summary
        with open(summary_filepath, 'w') as f:
            f.write(summary)
    else:
        raise Exception(f"summarize.py - request failed with status code {response.status_code}: {response.text}")

def start_server():
    # Start server
    command = f"{LLAMA_SERVER} -m {LLAMA_MODEL} -c {LLAMA_CONTEXT} --port {LLAMA_PORT} -ngl 999 -t 1 --log-disable"
    print(f"Executing command: {command}")
    process = subprocess.Popen(command.split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # process = subprocess.Popen(command.split()) # To see debug output
    time.sleep(5) # Wait time to start server and load model to GPUs
    return process

def stop_server(process):
    process.terminate()

def summarize_local(transcript_filepath, summary_filepath):
    try: 
        process = start_server()
        summarize(transcript_filepath, summary_filepath)
    except Exception as e: 
        print("summarize.py - An error occured during summarization")
        raise
    finally:
        stop_server(process)

if __name__ == "__main__":
    if len(sys.argv) < 3: print("Not enough arguments. Expected 'python record.py <job_index> <filename>'")
    summarize_local(sys.argv[1], sys.argv[2])