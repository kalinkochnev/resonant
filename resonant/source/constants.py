import math
import pyaudio
import source.geometry as geom

V_SOUND = 343  # speed of sound
NUM_SLICES = 20  # of slices to divide circle into
MIC_SPACING = 0.062  # meters
NUM_MICS = 4
SAMPLING_RATE = 48000  # of samples taken per second for each channel
WINDOW_SIZE = round(0.5 * SAMPLING_RATE) # This is the number of samples to run the algorithm on
# TODO not done
# 0 means no interpolation, 1 means one additional index for each amplitude
INTERPOLATION_AMOUNT = 0

AUDIO_FORMAT = pyaudio.paInt16
AUDIO_FRAME_SIZE = 1000 # We assume that there are this many samples for each microphone for the reading
LARGE_WINDOW = 5 * SAMPLING_RATE #  # of seconds times sampling rate

# The number of cycles for a sound to undergo localization/ML before disappearing it 
CYCLES_TO_LIVE = 6
CYCLES_INCONCLUSIVE = 3
SOURCE_MARGIN = geom.SphericalPt.angle_only(8) # Criteria to determine if a source falls within an existing source 

# MACHINE LEARNING
MIN_ML_SAMPLES, MAX_ML_SAMPLES = (1 * SAMPLING_RATE, 5 * SAMPLING_RATE) # The minimum number of samples to machine learn on, maximum allowed
ML_CONF_THRESH = 2 # # of standard deviations for a confidence to be to be conclusive

MIC_POSITIONS = [
    geom.SphericalPt(MIC_SPACING * math.sqrt(2), 5 * math.pi /4, 0),
    geom.SphericalPt(MIC_SPACING * math.sqrt(2), 3 * math.pi /4, 0),
    geom.SphericalPt(MIC_SPACING * math.sqrt(2), 1 * math.pi /4, 0),
    geom.SphericalPt(MIC_SPACING * math.sqrt(2), 7 * math.pi /4, 0),
]