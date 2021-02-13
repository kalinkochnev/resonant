import numpy as np
import pyaudio
import math

SPEED_OF_SOUND = 343
MIC_SEPARATION = 0.08182 # using diagonal pairs of mics
FORMAT = pyaudio.paInt16
CHANNELS = 4
RATE = 48000
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
def getAngle(r1, r2):
    
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
    

indicesToCheck = math.ceil((MIC_SEPARATION / SPEED_OF_SOUND) * RATE * 1.1) # we multiply by 1.1 as a safety factor

# yes this is the same code twice
# yes it should probably be a function or loop

maxCorr = -999999
maxCorrIndex = -999999
correlationValues = []
for i in range(-indicesToCheck, indicesToCheck):
    thisCorr = np.corrcoef(sig1, np.roll(sig3, i), 'valid')[0][1]
    correlationValues.append(thisCorr)
    if (thisCorr > maxCorr):
        maxCorr = thisCorr
        maxCorrIndex = i
ratio1 = max(min((-maxCorrIndex / RATE * SPEED_OF_SOUND) / MIC_SEPARATION, 1), -1)

maxCorr = -999999
maxCorrIndex = -999999
correlationValues = []
for i in range(-indicesToCheck, indicesToCheck):
    thisCorr = np.corrcoef(sig2, np.roll(sig4, i), 'valid')[0][1]
    correlationValues.append(thisCorr)
    if (thisCorr > maxCorr):
        maxCorr = thisCorr
        maxCorrIndex = i
ratio2 = max(min((-maxCorrIndex / RATE * SPEED_OF_SOUND) / MIC_SEPARATION, 1), -1)

angle1, angle2 = getAngle(ratio1, ratio2)
print(angle1, angle2)
print(aveAngle(angle1, angle2))

# one last thing
# you'll probably get a ton of errors with the respeaker sound card when you run
# I couldn't tell you what they mean, but they look like this:
# "ALSA lib pcm_hw.c:1822:(_snd_pcm_hw_open) Invalid value for card"