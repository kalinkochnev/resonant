import matplotlib.pyplot as plt
import numpy as np
import pyaudio
import math
from scipy.signal import argrelmax
from scipy.signal import savgol_filter

SPEED_OF_SOUND = 343
MIC_SEPARATION = 0.08182 # using diagonal pairs of mics
FORMAT = pyaudio.paInt16
CHANNELS = 4
RATE = 100000
CHUNK = 1024
RECORD_SECONDS = 2
 
audio = pyaudio.PyAudio()
 
# start Recording
stream = audio.open(format=FORMAT, channels=CHANNELS,
                rate=RATE, input=True,
                frames_per_buffer=CHUNK)
print ("recording...")
frames = []
 
for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    frames.append(data)
frames = b''.join(frames)
print ("finished recording")
 
 
# stop Recording
stream.stop_stream()
stream.close()
audio.terminate()

amplitude = np.frombuffer(frames, np.int16)
sig1 = amplitude[::4]
sig2 = amplitude[1::4]
sig3 = amplitude[2::4]
sig4 = amplitude[3::4]

# angles are weird, so if I'm not wrong, they need to be computed differently for each quadrent
# of course, I think there's still a better way to do this
# the angle is computed like on the unit circle, where 0 deg is directly between mics 3 and 4
def getAngle(i1, i2):
    r1 = max(min((-i1 / RATE * SPEED_OF_SOUND) / MIC_SEPARATION, 1), -1)
    r2 = max(min((-i2 / RATE * SPEED_OF_SOUND) / MIC_SEPARATION, 1), -1)
    
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

def diffAngle(a1, a2):
    diff = a1 - a2
    diff = (diff + 180) % 360 - 180
    return diff

print(diffAngle(320, 10))


def getCorrs(s1, s2):
    indicesToCheck = math.ceil((MIC_SEPARATION / SPEED_OF_SOUND) * RATE * 1.1) # we multiply by 1.1 as a safety factor
    correlationValues = []
    for i in range(-indicesToCheck, indicesToCheck):
        thisCorr = np.corrcoef(s1, np.roll(s2, i), 'valid')[0][1]
        correlationValues.append([i, thisCorr])
    return (correlationValues)

# get correlation values for every index offset
corrValues1 = getCorrs(sig1, sig3)
corrValues2 = getCorrs(sig2, sig4)

# find local maximums in the correlation values
relMax1 = argrelmax(np.array(corrValues1)) #[1,5,-8, 3]
relMax2 = argrelmax(np.array(corrValues2)) #[2, 8]

print(relMax1, relMax2)

combinations = np.array(np.meshgrid(relMax1, relMax2)).T.reshape(-1,2)

# indicesToCheck = math.ceil((MIC_SEPARATION / SPEED_OF_SOUND) * RATE * 1.1) # we multiply by 1.1 as a safety factor
# indexRange = range(-indicesToCheck, indicesToCheck)
# combinations = np.array(np.meshgrid(indexRange, indexRange)).T.reshape(-1,2)

# create a 3xN array with angle1, angle2 and relative confidence
possibleLocations = []
for i in combinations:
    angle1, angle2 = getAngle(corrValues1[i[0]][0], corrValues2[i[1]][0])
    correlation = ((corrValues1[i[0]][1]*corrValues2[i[1]][1])**2 / abs(diffAngle(angle1, angle2)))
    # possibleLocations.append([angle1, angle2, corrValues1[i[0]][1], corrValues2[i[1]][1]])
    possibleLocations.append([angle1, angle2, correlation])
possibleLocations = sorted(possibleLocations, key=lambda x: x[2])

for i in possibleLocations:
    print(i)

# one last thing
# you'll probably get a ton of errors with the respeaker sound card when you run
# I couldn't tell you what they mean, but they look like this:
# "ALSA lib pcm_hw.c:1822:(_snd_pcm_hw_open) Invalid value for card"