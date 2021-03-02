import math

V_SOUND = 343  # speed of sound
NUM_SLICES = 20  # of slices to divide circle into
MIC_SPACING = 0.062  # meters
NUM_MICS = 4
SAMPLING_RATE = 22050  # of samples taken per second for each channel
WINDOW_SIZE = 500 # This is the number of samples to run the algorithm on

# TODO not done
# 0 means no interpolation, 1 means one additional index for each amplitude
INTERPOLATION_AMOUNT = 0

import resonant.source.geometry as geom
MIC_POSITIONS = [
    geom.SphericalPt(MIC_SPACING * math.sqrt(2), 5 * math.pi /4, 0),
    geom.SphericalPt(MIC_SPACING * math.sqrt(2), 3 * math.pi /4, 0),
    geom.SphericalPt(MIC_SPACING * math.sqrt(2), 1 * math.pi /4, 0),
    geom.SphericalPt(MIC_SPACING * math.sqrt(2), 7 * math.pi /4, 0),
]