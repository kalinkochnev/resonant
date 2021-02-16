import math
import scipy.io.wavfile as wav
import numpy as np
from typing import List

V_SOUND = 338  # speed of sound
NUM_SLICES = 20  # of slices to divide circle into
MIC_SPACING = 0.062 /2 # meters
NUM_MICS = 4
SAMPLING_RATE = 348000  # of samples taken per second for each track

# TODO not done
# 0 means no interpolation, 1 means one additional index for each amplitude
INTERPOLATION_AMOUNT = 0


class SphericalPt:
    def __init__(self, radius, polar_angle, azimuth_angle):
        """The polar angle represents the rotation along the xy plane. Azimuth represents
        3D component from xy"""
        self.radius = radius
        self.polar = polar_angle
        self.azimuth = azimuth_angle

    def __str__(self):
        return f"Radius: {self.radius} -- Polar: {self.polar} -- Azimuth: {self.azimuth}"

    @classmethod
    def copy(cls, pt: 'SphericalPt') -> 'SphericalPt':
        return SphericalPt(pt.radius, pt.polar, pt.azimuth)

    def to_cartesian(self):
        x = self.radius * math.cos(self.azimuth) * math.cos(self.polar)
        y = self.radius * math.cos(self.azimuth) * math.sin(self.polar)
        z = self.radius * math.sin(self.azimuth)

        return (x, y, z)


class Mic:
    def __init__(self, audio: np.ndarray, position: SphericalPt):
        self.audio = audio
        self.original_audio = audio
        self.position: SphericalPt = position
        # in indices (to get approx. seconds, divide by sampling rate)
        self.audio_shift = 0

    @classmethod
    def from_recording(cls, num_mics: int, recording_path: str) -> List['Mic']:
        """Each track from a recording gets created into a new microphone. Returns list of mics"""
        microphones = []
        rate, recording = wav.read(recording_path)
        recording = recording.flatten()

        # This initializes mic objects with their channel and position
        for mic_index in range(0, NUM_MICS):
            angle_from_center = math.pi/4 + mic_index * \
                math.pi/2  # Generates angle for corner of square
            mic_pt = SphericalPt(MIC_SPACING/ 2 * math.sqrt(2), angle_from_center, 0)

            channel = recording[mic_index::NUM_MICS]
            microphones.append(Mic(np.array(channel), mic_pt))

        return microphones

    def shift_audio(self, seconds, fill_value=0) -> None:
        # TODO I assign a filler value of 0, which may skew the correlation. Room for improvement
        """Preallocates empty array and inserts previous array # of indices left or right
        with values to fill in the empty spots."""
        self.audio_shift += round(seconds *
                                  SAMPLING_RATE)  # of samples in that span of time

        shifted = np.empty_like(self.audio)
        if self.audio_shift > 0:
            shifted[:self.audio_shift] = fill_value
            shifted[self.audio_shift:] = self.audio[:-self.audio_shift]
        elif self.audio_shift < 0:
            shifted[self.audio_shift:] = fill_value
            shifted[:self.audio_shift] = self.audio[-self.audio_shift:]
        else:
            shifted[:] = self.audio
        # self.audio = np.roll(self.audio, self.audio_shift)
        self.audio = shifted

    def reset_shift(self):
        self.audio = self.original_audio
        self.audio_shift = 0

    def delay_from_source(self, source: SphericalPt) -> float:
        """This calculates the time delay that would occur if a sound was an infinite distance
        with an angle relative to the center of the microphones. Uses spherical coordinates
        Returns: delay in seconds

        Wolfram input: limit ( sqrt((s)^2 + (m)^2 - 2(s)(m)(sin(a)sin(b)cos(c-d)) +  cos(a)cos(b)    ) - s ) s-> infinity
        """
        mic_pos = self.position
        diff_in_azimuth = source.azimuth - mic_pos.azimuth
        return -mic_pos.radius * math.cos(diff_in_azimuth) * math.sin(source.polar) * math.sin(mic_pos.polar) / V_SOUND

    @classmethod
    def correlate(cls, a: 'Mic', b: 'Mic'):
        # Has to retrieve value from 2x2 matrix
        return np.corrcoef(a.audio, b.audio, 'valid')[0][1]


if __name__ == "__main__":
    file = 'experiments/respeaker_test_data/street_sounds_135_speech_270/combined.wav'
    print(f"Using file {file}")
    microphones = Mic.from_recording(4, file)

    # For each azimuth/height in a circle, loop through points of a circle.
    # Azimuth accounts for "changing" radius of a circle throughout a sphere

    correlated_pts: List[SphericalPt] = []
    for azimuth in np.linspace(0, math.pi/2, num=NUM_SLICES):
        print(azimuth)
        # angle relative to circle/polar
        for polar in np.linspace(0, 2 * math.pi, num=NUM_SLICES):
            src_pt = SphericalPt(0, polar, azimuth)
            # print(f"Calculating... {src_pt}")

            # Calc delays and subtract min from all shifts b/c it's as if it hits that mic first
            audio_shifts: np.ndarray = np.array([mic.delay_from_source(src_pt) for mic in microphones])
            
            # https://stackoverflow.com/questions/35215161/most-efficient-way-to-map-function-over-numpy-array
            audio_shifts -= audio_shifts.min()
            min_shift_index = audio_shifts.tolist().index(0)

            # Shift audios
            for mic_index in range(len(microphones)):
                mic = microphones[mic_index]
                shift = audio_shifts[mic_index]
                mic.shift_audio(shift)

            # Correlate microphones to "initial" mic. Remove that mic from mic array
            less_mics = microphones.copy()
            initial_mic = less_mics.pop(min_shift_index)

            avg_correlation = 0
            assert len(less_mics) == 3
            for mic in less_mics:
                correlation = Mic.correlate(initial_mic, mic)
                if correlation < 0:
                    correlation = 0
                avg_correlation += correlation / NUM_MICS

            # Set the radius = to the avg correlation for easier graphing
            src_pt.radius = avg_correlation
            correlated_pts.append(src_pt)

            # Reset the shifts of the microphone
            for mic in microphones:
                mic.reset_shift()

    # Put values on graph
    x, y, z = zip(*[pt.to_cartesian() for pt in correlated_pts])
    from mpl_toolkits.mplot3d import Axes3D
    from matplotlib import cm, colors
    import matplotlib.pyplot as plt
    import numpy as np

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    ax.scatter(x, y, z)

    plt.show()
