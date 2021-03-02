import math
from typing import List
from pathlib import Path

import pytest
import resonant.source.constants as resonant
import scipy.io.wavfile as wav
from resonant.source.geometry import SphericalPt
from resonant.source.initialization import AudioIter, OfflineAudioIter
import numpy as np


class TestBaseAudioIter:
    def test_split_channels(self):
        data = [1, 2, 3, 4, 1, 2, 3, 4]
        expected = [ [1, 1], [2, 2], [3, 3], [4, 4] ]
        a = AudioIter()
        assert a.split_into_channels(data) == expected

@pytest.fixture
def audio_file(tmp_path):
    def nested(data: List):
        file_path = tmp_path / "test.wav"
        wav.write(str(file_path), resonant.SAMPLING_RATE, np.array(data))
        return file_path
    return nested

@pytest.fixture
def offline_settings():
    resonant.SAMPLING_RATE = 3
    resonant.NUM_MICS = 3
    resonant.MIC_POSITIONS = [
        SphericalPt(1, 0, 0),
        SphericalPt(1, 2 * math.pi/3, 0),
        SphericalPt(1, 4 * math.pi/3, 0)
    ]

class TestOfflineAudioIter:
    def test_initialization(self, tmp_path: Path, audio_file, offline_settings):
        data = [1, 2, 3, 1, 2, 3, 1, 2, 3]
        file_path: Path = audio_file(data)

        audio_iter = OfflineAudioIter(str(file_path))

        expected_channels = [[1, 1, 1], [2, 2, 2], [3, 3, 3]]
        assert np.array_equal(audio_iter.audio_channels, expected_channels)

        mics = audio_iter.initialize_mics()
        for m, expected_pos in zip(mics, resonant.MIC_POSITIONS):
            assert m.signal.tolist() == np.zeros(0).tolist()
            assert m.position == expected_pos

    def test_single_iter(self, tmp_path: Path, audio_file, offline_settings):
        resonant.WINDOW_SIZE = 2
        resonant.NUM_MICS = 3
        data = [1, 2, 3, 1, 2, 3, 1, 2, 3]
        file_path: Path = audio_file(data)

        audio_iter = OfflineAudioIter(str(file_path))
        
        # Test 1 iteration
        result = next(audio_iter)
        expected = [np.array([1, 1]), np.array([2, 2]), np.array([3, 3])]
        assert np.array_equal(result, expected)

        # Test 2nd iteration
        result = next(audio_iter)
        expected = [np.array([1]), np.array([2]), np.array([3])]
        assert np.array_equal(result, expected)

    def test_stop_condition_loop(self, tmp_path: Path, audio_file, offline_settings):
        resonant.WINDOW_SIZE = 2
        resonant.NUM_MICS = 3
        data = [1, 2, 3, 1, 2, 3, 1, 2, 3]
        file_path: Path = audio_file(data)

        audio_iter = OfflineAudioIter(str(file_path))
        expec_iters = [
            [np.array([1, 1]), np.array([2, 2]), np.array([3, 3])],
            [np.array([1]), np.array([2]), np.array([3])],
        ]
        actual_iters: List[List[np.ndarray]] = []

        for channels in audio_iter:
            actual_iters.append(channels)
        
        for expec, actual in zip(expec_iters, actual_iters):
            assert np.array_equal(expec, actual)


