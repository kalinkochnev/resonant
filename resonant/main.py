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

        # if not live_audio.updated:
        #     to_remove = []
        #     for j in jobs:
        #         if not j.ready():
        #             to_remove.append(j)
        #         else:
        #             j.get()
        #             to_remove.append(j)
        #             break

        #     for j in to_remove:
        #         jobs.remove(j)

        #     continue
        localizer.update_signals(channels)
        # print(localizer.microphones[0].signal)

        start = time.time()
        # result = pool.apply_async(SourceLocalization.run_algorithm, (localizer.microphones,), callback=display)
        # jobs.append(result)
        # time.sleep(0.25)
        result = SourceLocalization.run_algorithm(localizer.microphones)
        # result = pool.apply(SourceLocalization.run_algorithm, (localizer.microphones,))
        src_scheduler.ingest(result)
        # result = pool.map_async(artificial_load, [1500], callback=lambda x: print('load run'))
        end = time.time()
        print(f"Load took {round(end - start, 3)}")
        # logging.debug(f"Load took {round(end - start, 3)}")
        # result = pool.map(SourceLocalization.run_algorithm, [localizer.microphones])[0]
        # print(result)

        #

    #         if curr_time - start_time >= 20:
    #             break
    # import scipy.io.wavfile as wavf
    # wavf.write('capturedaudio.wav', round(resonant.AUDIO_SAMPLING_RATE), localizer.microphones[0].signal)

    live_audio.stream.stop_stream()
    live_audio.stream.close()
    live_audio.pyaudio.terminate()


if __name__ == "__main__":
    program()
