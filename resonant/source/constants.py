import math
import pyaudio
import source.geometry as geom

ON_RP4 = True

# DEVICE SPECIFICATIONS
MIC_SPACING = 0.062  # meters
NUM_MICS = 4
MIC_POSITIONS = [
    geom.SphericalPt(MIC_SPACING * math.sqrt(2), 5 * math.pi /4, 0),
    geom.SphericalPt(MIC_SPACING * math.sqrt(2), 3 * math.pi /4, 0),
    geom.SphericalPt(MIC_SPACING * math.sqrt(2), 1 * math.pi /4, 0),
    geom.SphericalPt(MIC_SPACING * math.sqrt(2), 7 * math.pi /4, 0),
]

# AUDIO SETTINGS
AUDIO_INTERPOLATION = 0 # 0 means no interpolation, 1 means one additional index for each amplitude
AUDIO_FORMAT = pyaudio.paInt16
AUDIO_FRAME_SIZE = 1000 # We assume that there are this many samples for each microphone for the reading
AUDIO_SAMPLING_RATE = 44100  #  # of samples taken per second for each channel
FULL_WINDOW = 4 * AUDIO_SAMPLING_RATE #  # of seconds times sampling rate. Max number of samples to keep in memory

# The number of cycles for a sound to undergo localization/ML before disappearing it 
CYCLES_TO_LIVE = 6
CYCLES_INCONCLUSIVE = 3
SOURCE_MARGIN = geom.SphericalPt.angle_only(20) # Criteria to determine if a source falls within an existing source 

# MACHINE LEARNING
MIN_ML_SAMPLES, MAX_ML_SAMPLES = (0.5 * AUDIO_SAMPLING_RATE, 4 * AUDIO_SAMPLING_RATE) # The minimum number of samples to machine learn on, maximum allowed
ML_CONF_THRESH = 2 # # of standard deviations for a confidence to be to be conclusive
ML_SAMPLING_RATE = AUDIO_SAMPLING_RATE

# LOCALIZATON
LOCALIZATION_CORRELATION_THRESHOLD = 1e19
LOCALIZING_WINDOW = round(0.5 * AUDIO_SAMPLING_RATE) # This is the number of samples to run the algorithm on