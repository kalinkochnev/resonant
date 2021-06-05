import math
import threading
import time
from queue import LifoQueue, Queue
from typing import List

import numpy as np
import pyaudio
import scipy.io.wavfile as wav
from utils.arr import push_array

import source.constants as resonant
from source.mic import Mic
from source.threading import I2CLock


class AudioIter:
    """An iterator interface that returns audio based on a window size"""

    def __iter__(self):
        return self

    @classmethod
    def split_into_channels(cls, audio: np.ndarray):  # Takes flattened audio
        signals = []
        assert audio.size % resonant.NUM_MICS == 0, "Error flattened audio can't be split into channels"

        for mic_index in range(resonant.NUM_MICS):
            signals.append(audio[mic_index::resonant.NUM_MICS])
        return signals

    @classmethod
    def initialize_mics(cls) -> List[Mic]:
        microphones: List[Mic] = []
        for pos in resonant.MIC_POSITIONS:
            microphones.append(Mic(np.zeros(0), pos))

        return microphones

    def __next__(self):
        pass


class OfflineAudioIter(AudioIter):
    def __init__(self, file_path: str):
        self.audio_channels: List[np.ndarray] = self.load_channels(file_path)
        self.current_loc = 0  # Current location in terms of indices
        self.initialize_mics()

    @classmethod
    def load_channels(cls, path: str) -> List[np.ndarray]:
        rate, recording = wav.read(path)
        print(rate)
        assert rate == resonant.SAMPLING_RATE
        flattened = recording.flatten()
        return cls.split_into_channels(flattened)

    def __next__(self):
        signals: List[np.ndarray] = []
        window = resonant.LOCALIZING_WINDOW

        for sig in self.audio_channels:
            chunk = sig[self.current_loc:self.current_loc + window]
            if chunk.size != 0:
                signals.append(chunk)
            else:
                raise StopIteration
        self.current_loc += window

        return signals


class StreamProcessor:
    def __init__(self):
        # we make the queue size just slightly higher so we can take whatever doesn't divide easily and add that to the window to top it off
        max_queue_size = math.ceil(
            resonant.FULL_WINDOW / resonant.AUDIO_FRAME_SIZE)
        self.audio_queue = Queue(maxsize=max_queue_size)
        self.audio_channels: List[np.ndarray] = [
            np.zeros(resonant.FULL_WINDOW) for i in range(resonant.NUM_MICS)
        ]

    def flatten_queue(self):
        # We use -1 because the last item is used only for filling in the buffer window divisibility gap
        num_chunks = self.audio_queue.qsize()
        flattened_window = np.zeros(0)

        # This creates a flattened array of all the microphone readings
        for queue_index in range(num_chunks-1):
            chunk = self.audio_queue.get()  # Pop left is first in first out
            flattened_window = np.append(flattened_window, chunk)

        if num_chunks == self.audio_queue.maxsize:
            buffer_missing_samples = resonant.FULL_WINDOW % resonant.AUDIO_FRAME_SIZE

            # This fills in the readings for the # of mics to fill in the rest of the window
            leftover = self.audio_queue.get(
            )[:buffer_missing_samples * resonant.NUM_MICS]
            flattened_window = np.append(flattened_window, leftover)

        return flattened_window

    def cycle_channels(self, data: np.ndarray):
        # This does the equivalent of pushing new data to each channel
        channels = AudioIter.split_into_channels(data)
        for chan, new_audio in zip(self.audio_channels, channels):
            push_array(new_audio, chan, resonant.FULL_WINDOW)


class RealtimeAudio(StreamProcessor):
    def __init__(self, locks: I2CLock, audio_device=None):
        super().__init__()
        self.locks = locks
        self.pyaudio = pyaudio.PyAudio()
        self.acquire_stream(audio_device)

        self.stream.start_stream()

    def acquire_stream(self, audio_device):
        if audio_device is None:
            audio_device = self.choose_audio_device()

        self.locks.read.acquire()
        self.stream = self.pyaudio.open(format=resonant.AUDIO_FORMAT, channels=resonant.NUM_MICS,
                                        rate=resonant.AUDIO_SAMPLING_RATE, input=True,
                                        frames_per_buffer=resonant.AUDIO_FRAME_SIZE,
                                        input_device_index=audio_device)
        self.locks.read.release()

    def choose_audio_device(self):
        info = self.pyaudio.get_host_api_info_by_index(0)
        numdevices = info.get('deviceCount')
        for i in range(0, numdevices):
            if (self.pyaudio.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                print("Input Device id ", i, " - ",
                      self.pyaudio.get_device_info_by_host_api_device_index(0, i).get('name'))
        return int(input("What input id do you choose? "))

    def stream_reader(self):
        samples_avail = self.stream.get_read_available()

        while samples_avail < resonant.AUDIO_FRAME_SIZE:
            samples_avail = self.stream.get_read_available()

        assert samples_avail != 0
        # Acquires i2c lock and reads the audio stream
        self.locks.read.acquire()
        mic_bytes = self.stream.read(samples_avail, exception_on_overflow=False)

        self.locks.read.release()

        new_data = np.frombuffer(mic_bytes, dtype=np.int16)
        # Removes items from back of queue if it fills up
        if self.audio_queue.qsize() >= self.audio_queue.maxsize:
            self.audio_queue.get()

        self.audio_queue.put(new_data)

    def __iter__(self):
        return self

    def __next__(self):
        self.stream_reader()
        self.cycle_channels(self.flatten_queue())
        return self.audio_channels
