# import logging
import logging
import time
from threading import Lock, Thread

import numpy as np
import pyaudio
import scipy.io.wavfile

import source.constants as resonant
from source.algorithms import SourceLocalization
from source.hat import IMU, Hat
from source.initialization import AudioIter, OfflineAudioIter, RealtimeAudio
from source.mic import Source
from source.ml import AudioClassifier, SourceScheduler
from source.threading import I2CLock
from utils.arr import push_array


def setup_logging():
    logging.basicConfig(filename="log.txt", filemode="w+", level=logging.INFO)

def program():
    setup_logging()
    i2c_locks = I2CLock()

    # Init resources 
    ml = AudioClassifier()

    hat = Hat(i2c_locks)
    hat.sound_lock.start()
    hat.sound_lock.update_sound(90, "test")

    localizer = SourceLocalization(AudioIter.initialize_mics())
    src_scheduler = SourceScheduler(ml, hat)

    live_audio = RealtimeAudio(i2c_locks, audio_device=0)
    for channels in live_audio:
        localizer.update_signals(channels)
        src = localizer.run_algorithm()
        print(src)
        src_scheduler.ingest(src)

    live_audio.stream.stop_stream()
    live_audio.stream.close()
    live_audio.pyaudio.terminate()

if __name__ == "__main__":
    program()