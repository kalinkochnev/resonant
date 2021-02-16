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
MIC_SEPARATION = 0.08182 # using diagonal pairs of mics
FORMAT = pyaudio.paInt16
CHANNELS = 4
RATE = 44000
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

# waveFile = wave.open('combined.wav', 'wb')
# waveFile.setnchannels(CHANNELS)
# waveFile.setsampwidth(audio.get_sample_size(FORMAT))
# waveFile.setframerate(RATE)
# waveFile.writeframes(frames)
# waveFile.close()

amplitude = np.frombuffer(frames, np.int16)
sig = []
for i in range(CHANNELS):
    sig.append(amplitude[i::CHANNELS])

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

# again, we have to account for angle wrapping
def diffAngle(a1, a2):
    diff = a1 - a2
    diff = (diff + 180) % 360 - 180
    return diff

def getOffsets(a):
    m = MIC_SEPARATION / 4
    o1 = round((-m*math.sin(math.radians(a)) - m*math.cos(math.radians(a))) / SPEED_OF_SOUND * RATE)
    o2 = round((m*math.sin(math.radians(a)) - m*math.cos(math.radians(a))) / SPEED_OF_SOUND * RATE)
    o3 = round((m*math.sin(math.radians(a)) + m*math.cos(math.radians(a))) / SPEED_OF_SOUND * RATE)
    o4 = round((-m*math.sin(math.radians(a)) + m*math.cos(math.radians(a))) / SPEED_OF_SOUND * RATE)
    return [o1,o2,o3,o4]

correlationValues = []
allCorrs = []
for i in range(0,361, 5):
    print(i, end='\r')
    
    offsets = getOffsets(i)
    rsig = []
    for j in range(len(sig)):
        rsig.append(np.roll(sig[j], offsets[j]))

    correlation = 1
    allCorr = [i]
    for j in itertools.combinations(range(CHANNELS), 2):
        x, y = j
        c = np.corrcoef(rsig[x], rsig[y], 'valid')[1,0]
        # c = np.corrcoef(rsig[x], rsig[y], 'valid')[1,0] / (np.std(rsig[x]) * np.std(rsig[y]))
        correlation *= c
        allCorr.append(c)

    correlationValues.append([correlation, i, ])
    allCorrs.append(allCorr)

fig1 = plt.figure()
s1 = fig1.add_subplot(111, projection='polar')
s1.plot(np.array(correlationValues)[:,1]*(math.pi/180), np.array(correlationValues)[:,0])
fig1.savefig('correlation-computed.png')

print(allCorrs)

fig = plt.figure()
s = fig.add_subplot(111, projection='polar')
s.plot(np.array(allCorrs)[:,0]*(math.pi/180), np.array(allCorrs)[:,1])
s.plot(np.array(allCorrs)[:,0]*(math.pi/180), np.array(allCorrs)[:,2])
s.plot(np.array(allCorrs)[:,0]*(math.pi/180), np.array(allCorrs)[:,3])
s.plot(np.array(allCorrs)[:,0]*(math.pi/180), np.array(allCorrs)[:,4])
s.plot(np.array(allCorrs)[:,0]*(math.pi/180), np.array(allCorrs)[:,5])
s.plot(np.array(allCorrs)[:,0]*(math.pi/180), np.array(allCorrs)[:,6])
fig.savefig('correlations.png')



correlationValues = sorted(correlationValues, key=lambda x: x[0])
print (correlationValues)
