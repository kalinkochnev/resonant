from source.initialization import OfflineAudioIter, RealtimeAudio
from source.algorithms import CSPAnalysis
import source.constants as const
import pyaudio
import numpy as np
import time
import matplotlib.pyplot as plt
import scipy.io.wavfile

if __name__ == "__main__":
    # Load audio file
    audio_iter = OfflineAudioIter('../data/dog_barking_90/combined.wav')
    mics = audio_iter.initialize_mics()

    # Init resources
    # ml_resources = ml.init()
    algo = CSPAnalysis(mics)
    live_audio = RealtimeAudio()
    # fig = plt.figure()
    # ax = fig.add_subplot(111)
    # line, = ax.plot(live_audio.audio_channels[0])



def live():
    try:
        for a in live_audio:
            # print(int(live_audio.audio_channels[0].max()/30) *"|", end=100 * " " + "\r")
            # print(f"Len queue: {live_audio.audio_queue.qsize()}   Len window: {live_audio.audio_channels[0].size}")
            # print(f"max size {live_audio.audio_queue.maxsize}")
            # print(f"start of arr: {live_audio.audio_channels[0]}")
            # print(f"{live_audio.audio_queue.queue}")
            # plt.clf()
            # plt.plot(live_audio.audio_channels[0]) 
            # plt.pause(0.01)
            # plt.draw()
            algo.update_signals([np.copy(channel) for channel in live_audio.audio_channels])
            algo.run_algorithm()

    except Exception as e:
        print(e)
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
