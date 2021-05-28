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
from source.hat import Hat, IMU
import logging
from threading import Lock, Thread


def setup_logging():
    logging.basicConfig(filename="log.txt", filemode="w+", level=logging.INFO)

def program():
    setup_logging()

    # Init resources
    ml = AudioClassifier()

    hat = Hat()
    hat.sound_lock.start()
    hat.sound_lock.update_sound(0, "test")


    localizer = SourceLocalization(AudioIter.initialize_mics())
    live_audio = RealtimeAudio(audio_device=0)
    src_scheduler = SourceScheduler(ml, None)

    signal = np.zeros(resonant.MAX_ML_SAMPLES)
    for channels in live_audio:
        localizer.update_signals(channels)
        src = localizer.run_algorithm()
        src_scheduler.ingest(src)

    live_audio.stream.stop_stream()
    live_audio.stream.close()
    live_audio.pyaudio.terminate()

if __name__ == "__main__":
    imu = IMU()
    pyaudio = pyaudio.PyAudio()
    stream = pyaudio.open(format=resonant.AUDIO_FORMAT, channels=resonant.NUM_MICS,
                                    rate=resonant.AUDIO_SAMPLING_RATE, input=True,
                                    frames_per_buffer=resonant.AUDIO_FRAME_SIZE)
    lock = Lock()

    audio_data = []
    gyro_data = []

    def read_audio():
        
        while True:
            available = stream.get_read_available()
            if available == 0:
                continue
            lock.acquire()
            samples = stream.read(available)
            print(f"{len(samples)} ----------------")

            audio_data.append(samples)
            lock.release()


    def read_gyro():
        while True:
            lock.acquire()
            print("gyro")
            imu.readSensor()
            gyro_data.append(imu.GyroVals[2])
            lock.release()

    audio_thread = Thread(target=read_audio)
    imu_thread = Thread(target=read_gyro)
    
    stream.start_stream()
    audio_thread.start()
    imu_thread.start()

