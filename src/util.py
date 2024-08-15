import pyaudio

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
