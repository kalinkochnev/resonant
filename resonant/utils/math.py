import numpy as np
from numpy.fft import fft, ifft, fft2, ifft2, fftshift

def fft_crosscorr(x, y):
    f1 = fft(x)
    f2 = np.fft(np.flipud(y))
    cc = np.real(ifft(f1 * f2))
    return fftshift(cc)