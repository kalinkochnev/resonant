# import logging
import logging
import math
import multiprocessing as mp
import time
from multiprocessing import Pool, Process
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
from source.threads import I2CLock
from utils.arr import push_array


def setup_logging():
    logging.basicConfig(filename="log.txt", filemode="w", level=logging.DEBUG)


def artificial_load(upto=1000):
    return list(filter(lambda num: (num % np.arange(2, 1+int(math.sqrt(num)))).all(), range(2, upto+1)))


def program():
    setup_logging()
    i2c_locks = I2CLock()

    # Init resources
    ml = AudioClassifier()
    hat = Hat(i2c_locks)
    hat.sound_lock.start()

    localizer = SourceLocalization(AudioIter.initialize_mics())
    src_scheduler = SourceScheduler(ml, hat)

    live_audio = RealtimeAudio(i2c_locks, audio_device=0)

    def display(x):
        if x is not None:
            print(x)
        src_scheduler.ingest(x)

    # Starting threads
    live_audio.start()
    time.sleep(3)
    # jobs = []
    # with Pool(10) as pool:

    for channels in live_audio:
        if live_audio.audio_queue.empty():
            continue

        localizer.update_signals(channels)

        result = SourceLocalization.run_algorithm(localizer.microphones)
        src_scheduler.ingest(result)

    live_audio.stream.stop_stream()
    live_audio.stream.close()
    live_audio.pyaudio.terminate()


if __name__ == "__main__":
    program()
