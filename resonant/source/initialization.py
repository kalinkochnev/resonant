from typing import List

import numpy as np
import resonant.source.constants as resonant
import scipy.io.wavfile as wav
from resonant.source.mic import Mic


class AudioIter:
    """An iterator interface that returns audio based on a window size"""
    def __init__(self):
        self.initialize_mics()

    def __iter__(self):
        return self

    def split_into_channels(self, audio: np.ndarray):  # Takes flattened audio
        signals = []
        for mic_index in range(resonant.NUM_MICS):
            signals.append(audio[mic_index::resonant.NUM_MICS])
        return signals

    def initialize_mics(self) -> List[Mic]:
        pass

    def __next__(self):
        pass


class OfflineAudioIter(AudioIter):
    def __init__(self, file_path: str):
        self.audio_channels: List[np.ndarray] = self.load_channels(file_path)
        self.current_loc = 0  # Current location in terms of indices
        super().__init__()

    def load_channels(self, path: str) -> List[np.ndarray]:
        rate, recording = wav.read(path)
        assert rate == resonant.SAMPLING_RATE
        flattened = recording.flatten()
        return self.split_into_channels(flattened)

    def initialize_mics(self) -> List[Mic]:
        microphones: List[Mic] = []
        for pos in resonant.MIC_POSITIONS:
            microphones.append(Mic(np.zeros(0), pos))

        return microphones

    def __next__(self):
        signals: List[np.ndarray] = []
        window = resonant.WINDOW_SIZE

        for sig in self.audio_channels:
            chunk = sig[self.current_loc:self.current_loc + window]
            if chunk.size != 0:
                signals.append(chunk)
            else:
                raise StopIteration
        self.current_loc += window

        return signals
