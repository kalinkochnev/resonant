from source.initialization import AudioIter, OfflineAudioIter, RealtimeAudio
from source.algorithms import CSPAnalysis
from source.ml import SourceScheduler
import source.constants as const
import pyaudio
import numpy as np
import time
import matplotlib.pyplot as plt
import scipy.io.wavfile

if __name__ == "__main__":

    # Init resources
    # ml_resources = ml.init()
    localizer = CSPAnalysis(AudioIter.initialize_mics())
    live_audio = RealtimeAudio(audio_device=18)
    src_scheduler = SourceScheduler()

    for channels in live_audio:
        localizer.update_signals(channels)
        src  = localizer.run_algorithm()
        if src is not None:
            src_scheduler.ingest(src)

        # localizer.display_srcs()



    live_audio.stream.stop_stream()
    live_audio.stream.close()
    live_audio.pyaudio.terminate()


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
