import numpy as np
from tqdm import tqdm

def is_power(n):
	'''
	Checks if number is power of two
	
	Parameters
	----------
	n: real number

	Output
	----------
	boolean
	'''
	return (n & (n-1)) == 0

def ceil_pow(n):
	'''
	Returns the number whic is closest power of two
	
	Parameters
	----------
	n: real number
	
	Output
	----------
	n: real number
	'''
	if is_power(n):
		return n
	counter = 0
	while n != 0:
		n = n // 2
		counter += 1
	return 1 << counter

def alignment(x):
	'''
	Padds vector to its closest to power of two size
	
	Parameters
	----------
	x: numpy array
	
	Output 
	----------
	x: array padded with 0s
	'''
	if not is_power(x.size):
		n = ceil_pow(x.size)
		x = np.pad(x, (0, n-x.size), "constant", constant_values=(0,0))
	return x

def dft(x):
	'''
	Naive DFT with two for-loops
	
	Parameters
	----------
	x: array of real numbers
	
	Output 
	----------
	X: array of complex numbers
	'''
	N = np.size(x)
	X = np.zeros((N,), dtype=np.complex128)
	for m in range(0, N):
		for n in range(0, N):
			X[m] += x[n]*np.exp(-np.pi * 2j * m * n / N)
	return X

def fft(x):
    '''
    Fast Fourier Transformation
    
   	Parameters
   	----------
    x: array of real numbers
    
    Output
    ----------
    X: array of complex numbers
    '''
    n = np.size(x)
    if n == 1:
        return x
    a_even = fft(x[::2])
    a_odd = fft(x[1::2])   
    X = np.zeros((n,), dtype=np.complex128)
    k = n//2
    w_one =  np.exp(-2j * np.pi * 1 / n)
    w = 1 + 0j
    for i in range(k):
        X[i] += a_even[i] + w * a_odd[i]
        X[k + i] += a_even[i] - w * a_odd[i]
        w = w * w_one
    return X

def stft(x, window_size, step_size, one_sided=True):
	'''
	Short Time Fourier Transformation
	
	Parameters 
	----------
	x: numpy array of real numbers
	window_size: how many entries to analyze 
	step_size: size of steps
	one_sided: whether to return half of matrix
	
	Output
	---------- 
	spectrogramm: matrix of complex numbers
	'''
	if one_sided:
		frequency_size = window_size // 2 + 1
	else:
		frequency_size = window_size
	time_size = (x.size - window_size) // step_size + 1
	spectrogramm = np.zeros((time_size, frequency_size), dtype = np.complex128)
	for i in tqdm(range(time_size)):
		shift = i * step_size
		window_x = x[shift:shift + window_size]
		spectrogramm[i] = fft(window_x)[:frequency_size]
	return spectrogramm.T

def idft(X):
	'''
	Inverse DFT with two for-loops
	
	Parameters
	----------
	X: array of complex numbers
	
	Output 
	----------
	x: array of real numbers
	'''
	N = np.size(X)
	x = np.zeros((N,), dtype=np.complex128)
	for n in range(0, N):
		for m in range(0, N):
			x[n] += X[m]*np.exp(np.pi * 2j * m * n / N)
	return x / N

def ifft_recursive(X):
	'''
	Inverse Fast Fourier Transformation (recursion part)

	Parameters
	----------
    X: array of real numbers
	
	Output 
	----------
	x: array of complex numbers
	'''
	n = np.size(X)
	if n == 1:
		return X
	a_even = ifft_recursive(X[::2])
	a_odd = ifft_recursive(X[1::2])   
	x = np.zeros((n,), dtype=np.complex128)
	k = n//2
	for i in range(k):
		x[i] += a_even[i] + np.exp(2j * np.pi * i / n) * a_odd[i]
		x[k + i] += a_even[i] - np.exp(2j * np.pi * i / n) * a_odd[i]
	return x

def ifft(X):
	'''
    Inverse Fast Fourier Transformation (division by size part)
    
   	Parameters
   	----------
    X: array of complex numbers
    
    Output 
    ----------
    X: array of complex numbers
    '''
	X = np.array(X, dtype=np.complex128)
	return np.real(ifft_recursive(X)) / X.size

def istft(spectr, window_size_, step_size_, one_sided=True):
	'''
	Inverse Short Time Fourier Transformation
	
	Parameters 
	----------
	spectr: matrix of complex numbers
	window_size: how many entries to analyze 
	step_size: size of steps
	one_sided: whether to return half of matrix
	
	Output 
	----------
	signal: array of complex numbers
	'''
	if one_sided:
		sp_slice = spectr[-2:0:-1, :]
		sp_slice_ = np.conj(sp_slice)
		spectr = np.vstack([spectr, sp_slice_])
        
	spectr = spectr.T 
	time_size, freq_size = spectr.shape
	signal_size = (time_size - 1) * step_size_ + window_size_
	signal = np.zeros((signal_size,), dtype = np.complex128)
	counter_array = np.zeros((signal_size,), dtype = np.complex128)
    
	for i in range(time_size):
		shift = i * step_size_
		window_signal = ifft(spectr[i])
		signal[shift:shift + window_size_] += window_signal
		counter_array[shift:shift + window_size_] += 1
	signal = signal / counter_array
	return signal
