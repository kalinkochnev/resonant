import logging
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

def setup_logging():
    logging.basicConfig(filename="log.txt", filemode="a+", level=logging.DEBUG)

if __name__ == "__main__":
    setup_logging()

    # Init resources
    ml = AudioClassifier()
    localizer = SourceLocalization(AudioIter.initialize_mics())
    live_audio = RealtimeAudio()
    src_scheduler = SourceScheduler(ml)

    signal = np.zeros(resonant.MAX_ML_SAMPLES)
    for channels in live_audio:
        localizer.update_signals(channels)
        src = localizer.run_algorithm()
        src_scheduler.ingest(src)

    live_audio.stream.stop_stream()
    live_audio.stream.close()
    live_audio.pyaudio.terminate()

