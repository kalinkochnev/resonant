import matplotlib.pyplot as plt
import numpy as np
import pyaudio
import math
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
for i in range(0,361, 5):
    offsets = getOffsets(i)
    rsig1 = np.roll(sig1, offsets[0])
    rsig2 = np.roll(sig2, offsets[1])
    rsig3 = np.roll(sig3, offsets[2])
    rsig4 = np.roll(sig4, offsets[3])
    # if (i == 90):
    #     scipy.io.wavfile.write("mic1.wav", RATE, np.array(rsig1).astype(np.int16))
    #     scipy.io.wavfile.write("mic2.wav", RATE, np.array(rsig2).astype(np.int16))
    #     scipy.io.wavfile.write("mic3.wav", RATE, np.array(rsig3).astype(np.int16))
    #     scipy.io.wavfile.write("mic4.wav", RATE, np.array(rsig4).astype(np.int16))
    print(i, end='\r')
    c1= np.corrcoef(rsig1, rsig2, 'valid')[1,0]
    c2= np.corrcoef(rsig1, rsig3, 'valid')[1,0]
    c3= np.corrcoef(rsig1, rsig4, 'valid')[1,0]
    c4= np.corrcoef(rsig2, rsig3, 'valid')[1,0]
    c5= np.corrcoef(rsig2, rsig4, 'valid')[1,0]
    c6= np.corrcoef(rsig3, rsig4, 'valid')[1,0]

    correlation = c1**2+c2**2+c3**2+c4**2+c5**2+c6**2

    correlationValues.append([correlation/np.std([c1,c2,c3,c4,c5,c6]), i])

fig = plt.figure()
s = fig.add_subplot(111, projection='polar')
s.plot(np.array(correlationValues)[:,1]*(math.pi/180), np.array(correlationValues)[:,0])
fig.savefig('correlations.png')

correlationValues = sorted(correlationValues, key=lambda x: x[0])
print (correlationValues)
