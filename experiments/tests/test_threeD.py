import pytest
import experiments.threeD as settings
from experiments.threeD import Mic, SphericalPt
import math
import numpy as np


class TestSphericalPt:
    def test_to_cartesian(self):
        cartesian_coords = (3, 4, 5)
        spherical_coords = (7.0710678118655, 0.92729521800161,
                            math.pi/2 - 0.78539816339745)
        assert pytest.approx(SphericalPt(
            *spherical_coords).to_cartesian()) == cartesian_coords

    def test_copy(self):
        pt = SphericalPt(1, 2, 3)
        assert SphericalPt.copy(pt) == pt


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
        settings.SAMPLING_RATE = 1
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

        expected = 1 / settings.V_SOUND
        assert microphone.delay_from_source(src) == expected

    def test_reset_shift(self, mic_fixture):
        settings.SAMPLING_RATE = 1
        signal = np.array([1, 1, 1, 2, 2])

        microphone: Mic = mic_fixture(signal)
        microphone.shift_audio(2)
        assert not np.array_equal(microphone.audio, microphone.original_audio)

        microphone.reset_shift()
        assert microphone.audio_shift == 0
        assert np.array_equal(microphone.audio, signal)

    def test_delay_from_source_3D(self, mic_fixture)
