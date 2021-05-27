# import logging
import time

import numpy as np
import pyaudio
import scipy.io.wavfile

import source.constants as resonant
from source.algorithms import SourceLocalization
from source.initialization import AudioIter, OfflineAudioIter, RealtimeAudio
from source.mic import Source
from source.ml import AudioClassifier, SourceScheduler
from utils.arr import push_array
from source.hat import Hat


def test_lock():
    hat = Hat()
    hat.sound_lock.start()
    hat.sound_lock.update_sound(90, "dog bark")


if __name__ == "__main__":
    # setup_logging()
    hat = Hat()
    for i in range(360):
        hat.sound_lock.display_sound(i, "dog bark")

    # hat = Hat()
    # start_time = time.time()
    # while True:
    #     start_time, diffAngle = hat.sound_lock.integrate_gyro(start_time)
    #     print(
    #         f"Rel: {hat.sound_lock.rel_orientation}  abs: {hat.sound_lock.abs_orientation}")

    # Init resources
    # ml = AudioClassifier()
    # localizer = SourceLocalization(AudioIter.initialize_mics())
    # live_audio = RealtimeAudio()
    # src_scheduler = SourceScheduler(ml)

    # signal = np.zeros(resonant.MAX_ML_SAMPLES)
    # for channels in live_audio:
    #     localizer.update_signals(channels)
    #     src = localizer.run_algorithm()
    #     src_scheduler.ingest(src)

    # live_audio.stream.stop_stream()
    # live_audio.stream.close()
    # live_audio.pyaudio.terminate()
