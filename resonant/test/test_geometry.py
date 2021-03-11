import pytest
from source.geometry import SphericalPt
from source.mic import Mic
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


    def test_within_margin(self):
        origin = SphericalPt(1, 0, 0)
        margin = SphericalPt(1, 5, 4)

        # Test polar
        polar_inside = SphericalPt(1, 3, 0)
        assert origin.within_margin(margin, polar_inside) is True

        polar_outside = SphericalPt(1, 6.1, 0)
        polar_outside_neg = SphericalPt(1, -6.1, 0)
        assert origin.within_margin(margin, polar_outside) is False
        assert origin.within_margin(margin, polar_outside_neg) is False

        # Test azimuth
        polar_inside = SphericalPt(1, 0, 3)
        assert origin.within_margin(margin, polar_inside) is True

        polar_outside = SphericalPt(1, 0, 4.1)
        polar_outside_neg = SphericalPt(1, 0, -4.1)
        assert origin.within_margin(margin, polar_outside) is False
        assert origin.within_margin(margin, polar_outside_neg) is False
