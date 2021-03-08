from source.initialization import OfflineAudioIter
from source.algorithms import SphereTester
import source.constants as const
import pyaudio
import numpy as np
import time

lw_size = const.SAMPLING_RATE * const.LARGE_WINDOW
large_window = np.zeros(lw_size)


def reader(in_data, frame_count, time_info, status):
    global large_window
    new_data = np.frombuffer(in_data, dtype=np.int16)
    updated = np.concatenate((new_data, large_window[:lw_size-frame_count]))
    large_window = updated
    print(f"{large_window} ---- size: {large_window[large_window !=0].size} ----- arr siez {large_window.size}")

    return (in_data, pyaudio.paContinue)


def choose_audio_device(p_audio):
    info = p_audio.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')
    for i in range(0, numdevices):
        if (p_audio.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
            print("Input Device id ", i, " - ",
                  p_audio.get_device_info_by_host_api_device_index(0, i).get('name'))
    return int(input("What input id do you choose?"))


if __name__ == "__main__":
    # Load audio file
    audio_iter = OfflineAudioIter('../data/dog_barking_90/combined.wav')
    mics = audio_iter.initialize_mics()
    """localization = SphereTester(mics)

    for window in audio_iter:
        localization.update_signals(window)
        localization.run()"""

    # Init resources
    # ml_resources = ml.init()
    py_aud = pyaudio.PyAudio()
    audio_stream = py_aud.open(format=const.AUDIO_FORMAT, channels=const.NUM_MICS,
                               rate=const.SAMPLING_RATE, input=True, frames_per_buffer=const.AUDIO_FRAME_SIZE, 
                               stream_callback=reader, input_device_index=choose_audio_device(py_aud))
    audio_stream.start_stream()
    while audio_stream.is_active():
        time.sleep(0.2)

    audio_stream.stop_stream()
    audio_stream.close()
    py_aud.terminate()

    # Main thread that reads audio

    # LOCATOR THREAD: reads data into buffer

    # if sound is localized
    # Add untracked source
    # start ML thread

    # ML Reader: reads data into buffer
    # Once evaluation time (buffer is filled or updated)
    # for un/tracked sounds
    # Beamform sound and start ML THREAD:
    # evaluate model. If sound found, return sound

    # If sound is found
    # add tracked source

    # Back to locator
