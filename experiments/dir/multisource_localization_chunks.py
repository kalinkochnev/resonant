import matplotlib.pyplot as plt
import numpy as np
import pyaudio
import math
import itertools
from scipy.signal import argrelmax
from scipy.signal import savgol_filter
import wave
import scipy.io.wavfile

SPEED_OF_SOUND = 343
MIC_SEPARATION = 0.08182  # using diagonal pairs of mics
FORMAT = pyaudio.paInt16
CHANNELS = 4
RATE = 44000
CHUNK = 1024
RECORD_SECONDS = 2

PROCESSING_CHUNK_LENGTH = 500

# audio = pyaudio.PyAudio()

# # start Recording
# stream = audio.open(format=FORMAT, channels=CHANNELS,
#                     rate=RATE, input=True,
#                     frames_per_buffer=CHUNK)
# print("recording...")
# frames = []

# for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
#     data = stream.read(CHUNK)
#     frames.append(data)
# frames = b''.join(frames)
# print("finished recording")


# # stop Recording
# stream.stop_stream()
# stream.close()
# audio.terminate()

# amplitude = np.frombuffer(frames, np.int16)
# sig = []
# for i in range(CHANNELS):
#     sig.append(amplitude[i::CHANNELS])

RATE, data = scipy.io.wavfile.read("../respeaker_test_data/dog_barking_90_speech_270/combined.wav")
sig = []
data = data[::35]
for i in range(CHANNELS):
    sig.append(data[:,i])

# angles are weird, so if I'm not wrong, they need to be computed differently for each quadrent
# of course, I think there's still a better way to do this
# the angle is computed like on the unit circle, where 0 deg is directly between mics 3 and 4


def getAngle(s1, s2):
    r1 = max(min((-s1 * SPEED_OF_SOUND) / MIC_SEPARATION, 1), -1)
    r2 = max(min((-s2 * SPEED_OF_SOUND) / MIC_SEPARATION, 1), -1)

    if (r1 >= 0 and r2 >= 0):
        angle1 = -math.acos(r1) * (180/math.pi) + 225
        angle2 = math.acos(r2) * (180/math.pi) + 135
    elif (r1 <= 0 and r2 <= 0):
        angle1 = math.acos(r1) * (180/math.pi) - 135
        angle2 = -math.acos(r2) * (180/math.pi) + 135
    elif (r1 > 0 and r2 < 0):
        angle1 = math.acos(r1) * (180/math.pi) - 135
        angle2 = math.acos(r2) * (180/math.pi) + 135
    elif (r1 < 0 and r2 > 0):
        angle1 = -math.acos(r1) * (180/math.pi) + 225
        angle2 = -math.acos(r2) * (180/math.pi) + 135

    if (angle1 < 0):
        angle1 += 360
    if (angle2 < 0):
        angle2 += 360

    return angle1, angle2

# we have to account for angle wrapping when averaging
# e.g. aveAngle(350, 10) = 360 and not 180


def aveAngle(a1, a2):
    if (a1 < 90 and a2 > 270):
        a1 -= 360
    if (a2 < 90 and a1 > 270):
        a2 -= 360

    ave = (a1 + a2) / 2

    if (ave < 0):
        ave += 360

    return ave

# again, we have to account for angle wrapping


def diffAngle(a1, a2):
    diff = a1 - a2
    diff = (diff + 180) % 360 - 180
    return diff


def getShift(sig1, sig2):
    # we multiply by 1.1 as a safety factor
    indicesToCheck = math.ceil((MIC_SEPARATION / SPEED_OF_SOUND) * RATE * 1.1)
    maxCorr = -1.0
    maxCorrIndex = 0
    for i in range(-indicesToCheck, indicesToCheck):
        thisCorr = np.corrcoef(sig1, np.roll(sig2, i), 'valid')[0][1]
        if thisCorr > maxCorr:
            maxCorr = thisCorr
            maxCorrIndex = i

    return ([maxCorrIndex / RATE, maxCorr])


chunk = [0, 0, 0, 0]
shiftList = []
for i in range(0, len(sig[0]), PROCESSING_CHUNK_LENGTH):
    print(i/len(sig[0]), end = "\r")
    chunk[0] = sig[0][i:i+PROCESSING_CHUNK_LENGTH]
    chunk[1] = sig[1][i:i+PROCESSING_CHUNK_LENGTH]
    chunk[2] = sig[2][i:i+PROCESSING_CHUNK_LENGTH]
    chunk[3] = sig[3][i:i+PROCESSING_CHUNK_LENGTH]

    # correlation = [getShift(chunk[0], chunk[1]), getShift(chunk[0], chunk[2]), getShift(
    #     chunk[0], chunk[3]), getShift(chunk[1], chunk[2]), getShift(chunk[1], chunk[3]), getShift(chunk[2], chunk[3])]
    shifts = [getShift(chunk[0], chunk[2])[0], getShift(chunk[1], chunk[3])[0]]
    if (getShift(chunk[0], chunk[2])[1] + getShift(chunk[0], chunk[2])[1] > 0.5):
        shiftList.append(shifts)

angleList = []
for i in shiftList:
    angle1, angle2 = getAngle(i[0], i[1])
    angleList.append(aveAngle(angle1, angle2))
    # angleList.append(angle1)
    # angleList.append(angle1)

angleList = np.array(angleList)
angle = math.atan2(sum(np.sin(angleList * (np.pi / 180))), sum(np.cos(angleList * (np.pi / 180)))) * (180 / np.pi)

print(angle)

def circular_hist(ax, x, bins=16, density=True, offset=0, gaps=True):
    """
    Produce a circular histogram of angles on ax.

    Parameters
    ----------
    ax : matplotlib.axes._subplots.PolarAxesSubplot
        axis instance created with subplot_kw=dict(projection='polar').

    x : array
        Angles to plot, expected in units of radians.

    bins : int, optional
        Defines the number of equal-width bins in the range. The default is 16.

    density : bool, optional
        If True plot frequency proportional to area. If False plot frequency
        proportional to radius. The default is True.

    offset : float, optional
        Sets the offset for the location of the 0 direction in units of
        radians. The default is 0.

    gaps : bool, optional
        Whether to allow gaps between bins. When gaps = False the bins are
        forced to partition the entire [-pi, pi] range. The default is True.

    Returns
    -------
    n : array or list of arrays
        The number of values in each bin.

    bins : array
        The edges of the bins.

    patches : `.BarContainer` or list of a single `.Polygon`
        Container of individual artists used to create the histogram
        or list of such containers if there are multiple input datasets.
    """
    # Wrap angles to [-pi, pi)
    x = (x+np.pi) % (2*np.pi) - np.pi

    # Force bins to partition entire circle
    if not gaps:
        bins = np.linspace(-np.pi, np.pi, num=bins+1)

    # Bin data and record counts
    n, bins = np.histogram(x, bins=bins)

    # Compute width of each bin
    widths = np.diff(bins)

    # By default plot frequency proportional to area
    if density:
        # Area to assign each bin
        area = n / x.size
        # Calculate corresponding bin radius
        radius = (area/np.pi) ** .5
    # Otherwise plot frequency proportional to radius
    else:
        radius = n

    # Plot data on ax
    patches = ax.bar(bins[:-1], radius, zorder=1, align='edge', width=widths,
                     edgecolor='C0', fill=False, linewidth=1)

    # Set the direction of the zero angle
    ax.set_theta_offset(offset)

    # Remove ylabels for area plots (they are mostly obstructive)
    if density:
        ax.set_yticks([])

    return n, bins, patches

# Construct figure and axis to plot on
fig, ax = plt.subplots(subplot_kw=dict(projection='polar'))

# Visualize by area of bins
circular_hist(ax, angleList * math.pi/180, density=False)

fig.savefig('angleHist.png')

# x = 2 (math.atan((sqrt(2 m**2 - d**2) - m)/(d + m)) + math.pi)

# for i in range(0, 360, 10):