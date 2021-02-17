import pytest
from experiments.threeD import Mic, SphericalPt
import math
class TestSphericalPt:
    def test_to_cartesian(self):
        cartesian_coords = (3, 4, 5)
        spherical_coords = (7.0710678118655, 0.92729521800161, math.pi/2 - 0.78539816339745)
        assert pytest.approx(SphericalPt(*spherical_coords).to_cartesian()) == cartesian_coords

    def test_copy(self):
        pt = SphericalPt(1, 2, 3)
        assert SphericalPt.copy(pt) == pt

@pytest.fixture
def mic():
    def mic(signal):
        src = SphericalPt(1, math.pi/4, math.pi/4)
        return Mic(signal, src)

class TestMic:
    def test_shift(self, mic):
        src