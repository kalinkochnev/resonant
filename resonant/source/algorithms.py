from typing import List
from resonant.source.mic import Mic
import resonant.source.constants as resonant
import numpy as np


class Algorithm:  # Abstract class to implement algorithms:
    def __init__(self, microphones):
        self.microphones: List[Mic] = microphones

    @property
    def pairs(self):
        # Assumes every other microphone is a "pair"
        evens = self.microphones[::2]
        odds = self.microphones[1::2]

        # https://stackoverflow.com/questions/1624883/alternative-way-to-split-a-list-into-groups-of-n
        def grouper(arr, group_size): return zip(*(iter(arr),) * group_size)

        return [*grouper(evens, 2), *grouper(odds, 2)]

    def update_signals(self, signals: List[np.ndarray]):
        signals = self.interpolate_signals(signals)  # Pre-process signals

        for mic, sig in zip(self.microphones, signals):
            mic.signal = sig

    def interpolate_signals(self, signals):
        """This duplicates each element in the array for example,
        [1, 2, 3] becomes [1, 1, 2, 2, 3, 3] depending on the interpolation
        amount specified in constants"""

        # This is + 1 b/c you have to include the original signal in the interpolation
        interp_amount = resonant.INTERPOLATION_AMOUNT + 1 
        if interp_amount == 0:
            return signals

        interpolated = []
        for sig in signals:
            temp = np.empty(sig.size * interp_amount)
            for i in range(interp_amount):
                temp[i::interp_amount] = sig

            interpolated.append(temp)
        return interpolated

    def run(self):
        raise NotImplementedError("You need to run a subclass of this class!")


class SphereTester(Algorithm):
    pass
