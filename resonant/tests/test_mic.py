
import math

import numpy as np
import pytest
from resonant.source.geometry import SphericalPt
from resonant.source.mic import Mic
import resonant.source.constants as resonant


@pytest.fixture
def mic_fixture():
    def mic(signal):
        src = SphericalPt(1, math.pi/4, math.pi/4)
        return Mic(signal, src)
    return mic


class TestMic:
    @pytest.mark.parametrize("shift, expected", [
        (0, [1, 1, 1, 2, 2]),
        (2, [0, 0, 1, 1, 1]),
        (-2, [1, 2, 2, 0, 0])
    ])
    def test_shift(self, shift, expected, mic_fixture):
        resonant.SAMPLING_RATE = 1
        signal = np.array([1, 1, 1, 2, 2])

        microphone: Mic = mic_fixture(signal)
        microphone.shift_audio(shift)

        assert np.array_equal(microphone.audio, np.array(expected))
        assert microphone.audio_shift == shift

    def test_delay_from_source(self, mic_fixture):
        signal = np.array([1, 1, 1, 2, 2])

        # 2d first, top left corner of square first
        angle = math.pi/4
        microphone: Mic = mic_fixture(signal)
        microphone.position = SphericalPt(1, math.pi/4, 0)
        src = SphericalPt(1, math.pi/4, 0)

        expected = 1 / resonant.V_SOUND
        assert microphone.delay_from_source(src) == expected

    def test_reset_shift(self, mic_fixture):
        resonant.SAMPLING_RATE = 1
        signal = np.array([1, 1, 1, 2, 2])

        microphone: Mic = mic_fixture(signal)
        microphone.shift_audio(2)
        assert not np.array_equal(microphone.audio, microphone.original_audio)

        microphone.reset_shift()
        assert microphone.audio_shift == 0
        assert np.array_equal(microphone.signal, signal)
