from typing import List
import numpy as np
import math
from source.geometry import SphericalPt
import source.constants as resonant
from numpy.fft import fft, ifft, fft2, ifft2, fftshift


class Mic:
    def __init__(self, audio: np.ndarray, position: SphericalPt):
        self.signal = audio
        self.original_audio = audio
        self.position: SphericalPt = position
        self.audio_shift = 0

    def shift_audio(self, seconds, fill_value=0) -> None:
        # TODO I assign a filler value of 0, which may skew the correlation. Room for improvement
        """Preallocates empty array and inserts previous array # of indices left or right
        with values to fill in the empty spots."""
        self.audio_shift += round(seconds *
                                  resonant.SAMPLING_RATE)  # of samples in that span of time

        shifted = np.empty_like(self.signal)
        if self.audio_shift > 0:
            shifted[:self.audio_shift] = fill_value
            shifted[self.audio_shift:] = self.signal[:-self.audio_shift]
        elif self.audio_shift < 0:
            shifted[self.audio_shift:] = fill_value
            shifted[:self.audio_shift] = self.signal[-self.audio_shift:]
        else:
            shifted[:] = self.signal
        # self.audio = np.roll(self.audio, self.audio_shift)
        self.audio = shifted

    def reset_shift(self):
        self.signal = self.original_audio
        self.audio_shift = 0

    def delay_from_source(self, source: SphericalPt) -> float:
        """This calculates the time delay that would occur if a sound was an infinite distance
        with an angle relative to the center of the microphones. Uses spherical coordinates
        Returns: delay in seconds

        limit ( s - sqrt((s)^2 + (m)^2 - 2(s)(m)(sin(a)sin(b)cos((pi/2-c)-(pi/2-d)) +  cos(a)cos(b)   ) ) ) s-> infinity        
        """
        mic_pos = self.position
        diff_in_azimuth = source.azimuth - mic_pos.azimuth
        if diff_in_azimuth == 0:  # Hopefully optimized when azimuth is 0
            return mic_pos.radius * math.cos(source.polar - mic_pos.polar) / resonant.V_SOUND
        else:
            return mic_pos.radius * (math.cos(source.polar) * math.cos(mic_pos.polar) + math.cos(diff_in_azimuth) * math.sin(source.polar) * math.sin(mic_pos.polar)) / resonant.V_SOUND

    @classmethod
    def correlate(cls, a: 'Mic', b: 'Mic'):
        # Has to retrieve value from 2x2 matrix
        # https://lexfridman.com/fast-cross-correlation-and-time-series-synchronization-in-python/
        f1 = fft(a.signal)
        f2 = fft(np.flipud(b.signal))
        cc = np.real(ifft(f1 * f2))
        return fftshift(cc)

class Source:
    def __init__(self, position):
        self.tracked = False
        self.position: SphericalPt = position
        self.audio = np.empty()