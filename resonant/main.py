from source.initialization import AudioIter, OfflineAudioIter, RealtimeAudio
from source.algorithms import SourceLocalization
from source.ml import SourceScheduler, AudioClassifier
import source.constants as resonant
import pyaudio
import numpy as np
import time
import matplotlib.pyplot as plt
import scipy.io.wavfile
from utils.arr import push_array
from source.mic import Source

if __name__ == "__main__":

    # Init resources
    ml = AudioClassifier()
    localizer = SourceLocalization(AudioIter.initialize_mics())
    live_audio = RealtimeAudio(audio_device=0)
    src_scheduler = SourceScheduler(ml)

    signal = np.zeros(resonant.MAX_ML_SAMPLES)
    for channels in live_audio:
        localizer.update_signals(channels)
        src = localizer.run_algorithm()
        src_scheduler.ingest(src)

        # print(len(live_audio.blah))
        # np.array(live_audio.blah[1::resonant.NUM_MICS].astype(np.int16)
        # scipy.io.wavfile.write("ml.wav", resonant.SAMPLING_RATE, live_audio.audio_channels[0].astype(np.int16))
        # time.sleep(2)
        # print('saved')






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
