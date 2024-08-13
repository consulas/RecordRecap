import os
import yaml
import pyaudio

with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Access constants 
MODELS_DIR = config["MODELS_DIR"]
DATA_DIR = config["DATA_DIR"]
RECORDINGS_DIR = config["RECORDINGS_DIR"]
TRANSCRIPTS_DIR = config["TRANSCRIPTS_DIR"]
SUMMARIES_DIR = config["SUMMARIES_DIR"]
# CONTEXTS_DIR = config["CONTEXTS_DIR"]

def create_path(path: str):
    if os.path.exists(path):
        print(f"Path exists: {path}")
    else:
        os.makedirs(path, exist_ok=True)
        print(f"Created path: {path}")

def get_positive_int(prompt):
    while True:
        try:
            value = int(input(prompt))
            if value < 0:
                print("Please enter a non-negative number.")
            else:
                return value
        except ValueError:
            print("Please enter a valid number.")

def get_device_info():
    audio = pyaudio.PyAudio()
    info = audio.get_host_api_info_by_index(0)
    num_devices = info.get('deviceCount')
    device_info_arr = []

    for i in range(num_devices):
        device_info = audio.get_device_info_by_host_api_device_index(0, i)
        max_input_channels = device_info.get('maxInputChannels')
        if max_input_channels > 0:
            device_name = device_info.get('name')
            device_info_arr.append({"device_index":i, "device_name":device_name, "num_channels":max_input_channels})

    return device_info_arr

def get_device_selection(device_info):
    print("Available devices:")
    for device in device_info:
        print(f"Device Index: {device["device_index"]} - Device Name: {device["device_name"]} - Num Channels: {device["num_channels"]}")
    
    while True:
        try:
            selected_id = int(input("Select a device by index: "))
            selected_device = next((d for d in device_info if d["device_index"] == selected_id), None)
            if selected_device is None:
                print("Invalid device ID. Please try again.")
            else:
                return selected_device
        except ValueError:
            print("Please enter a valid number.")

def get_channel_choice(num_channels):
    if num_channels > 1:
        print("Note: This device has multiple channels. It is most common to have 2 for L/R stereo or 1 for mono.")
        while True:
            choice = get_positive_int("Select 1 to record all channels (L/R), or 0 for specific channel: ")
            if choice == 1:
                return (choice, 0)
            elif choice == 0:
                while True:
                    print()
                    if num_channels == 2: print("There are two channels - enter 0 for left and 1 for right")
                    specific_channel = get_positive_int(f"Select a specific channel to save (0 <= n < {num_channels}):")
                    if 0 <= specific_channel < num_channels:
                        return (num_channels, specific_channel)
                    else:
                        print("Invalid channel number. Please try again.")
            else:
                print("Please select 1 or 0.")
    return (num_channels, 0)

def create_config():
    device_info = get_device_info()
    job_device_config = {}
    num_jobs = get_positive_int("How many jobs do you have? ")


    for job_index in range(1, num_jobs+1):
        company_name = input(f"\nEnter the company name for job #{job_index}: ")
        num_devices = get_positive_int("How many devices are you recording from? (For separate mic + meeting audio devices, put 2; otherwise just put 1): ")

        devices_config = []
        for device_idx in range(num_devices):
            print()
            print(f"Select audio device #{device_idx+1} for {company_name}")
            selected_device = get_device_selection(device_info)
            print()
            num_channels, channel = get_channel_choice(selected_device["num_channels"])
            device_config = {
                "device_name": selected_device["device_name"],
                "device_index": selected_device["device_index"],
                "num_channels": num_channels,
                "channel": channel
            }

            devices_config.append(device_config)
        job_device_config[job_index] = {"company": company_name, "devices": devices_config}
            
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    config["JOB_DEVICE_MAPPINGS"] = job_device_config

    with open('config.yaml', 'w') as f:
        yaml.dump(config, f, sort_keys=False)

def main():
    create_path(MODELS_DIR)
    create_path(DATA_DIR)
    create_path(RECORDINGS_DIR)
    create_path(TRANSCRIPTS_DIR)
    create_path(SUMMARIES_DIR)
    # create_path(CONTEXTS_DIR)

    create_config()

if __name__ == "__main__":
    main()
