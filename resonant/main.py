from source.initialization import AudioIter, OfflineAudioIter, RealtimeAudio
from source.algorithms import CSPAnalysis
import source.constants as const
import pyaudio
import numpy as np
import time
import matplotlib.pyplot as plt
import scipy.io.wavfile

if __name__ == "__main__":
    # Load audio live_audiofile
    # audio_iter = OfflineAudioIter('../data/street_sounds_135/combined.wav')
    # mics = audio_iter.initialize_mics()

    # Init resources
    # ml_resources = ml.init()
    algo = CSPAnalysis(AudioIter.initialize_mics())
    live_audio = RealtimeAudio()

    for channels in live_audio:
        # plt.clf()
        # plt.plot(live_audio.audio_channels[0]) 
        # plt.pause(0.01)
        # plt.draw()
        algo.update_signals([np.copy(channel[0:const.WINDOW_SIZE]) for channel in channels])
        # algo.update_signals(a)
        algo.run_algorithm()
        # time.sleep(2)

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
