import pytest
from resonant.source.mic import Mic
from resonant.source.geometry import SphericalPt
from resonant.source.algorithms import Algorithm
import resonant.source.constants as resonant
import numpy as np

@pytest.mark.parametrize("signal, expected", [
    [[1, 2, 3, 4], [1, 1, 2, 2, 3, 3, 4, 4]],
    [[1, 2, 3], [1, 1, 2, 2, 3, 3]],
])
def test_interpolation(signal, expected):
    resonant.INTERPOLATION_AMOUNT = 1
    signal = np.array(signal)
    mic = Mic(signal, SphericalPt(1, 0, 0))
    
    algo = Algorithm([mic])
    result = algo.interpolate_signals([signal])
    assert result[0].tolist() == np.array(expected).tolist()

