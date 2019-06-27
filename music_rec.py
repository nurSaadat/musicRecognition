import argparse
import datetime
import librosa
import logging
import matplotlib.pyplot as plt
import my_ft_lib as mylib
import numpy as np
import soundfile as sf
import os
import pylab
from tqdm import tqdm

NOTES = {
	"C_0" : 16.35,
	"C#0" : 17.32,
	"D_0" : 18.35,
	"D#0" : 19.45,
	"E_0" : 20.60,
	"F_0" : 21.83,
	"F#0" : 23.12,
	"G_0" : 24.50,
	"G#0" : 25.96,
	"A_0" : 27.50,
	"A#0" : 29.14,
	"B_0" : 30.87,
	"C_1" : 32.70,
	"C#1" : 34.65,
	"D_1" : 36.71,
	"D#1" : 38.89,
	"E_1" : 41.20,
	"F_1" : 43.65,
	"F#1" : 46.25,
	"G_1" : 49.00,
	"G#1" : 51.91,
	"A_1" : 55.00,
	"A#1" : 58.27,
	"B_1" : 61.74,
	"C_2" : 65.41,
	"C#2" : 69.30,
	"D_2" : 73.42,
	"D#2" : 77.78,
	"E_2" : 82.41,
	"F_2" : 87.31,
	"F#2" : 92.50,
	"G_2" : 98.00,
	"G#2" : 103.83,
	"A_2" : 110.00,
	"A#2" : 116.54,
	"B_2" : 123.47,
	"C_3" : 130.81,
	"C#3" : 138.59,
	"D_3" : 146.83,
	"D#3" : 155.56,
	"E_3" : 164.81,
	"F_3" : 174.61,
	"F#3" : 185.00,
	"G_3" : 196.00,
	"G#3" : 207.65,
	"A_3" : 220.00,
	"A#3" : 233.08,
	"B_3" : 246.94,
	"C_4" : 261.63,
	"C#4" : 277.18,
	"D_4" : 293.66,
	"D#4" : 311.13,
	"E_4" : 329.63,
	"F#4" : 369.99,
	"G_4" : 392.00,
	"G#4" : 415.30,
	"A_4" : 440.00,
	"A#4" : 466.16,
	"B_4" : 493.88,
	"C_5" : 523.25,
	"D_5" : 587.33,
	"D#5" : 622.25,
	"E_5" : 659.25,
	"F_5" : 698.46,
	"G_5" : 783.99,
	"G#5" : 830.61,
	"A_5" : 880.00,
	"A#5" : 932.33,
	"B_5" : 987.77
}

KEYS = [
	"C_3", 
	"C#3",
	"D_3",
	"D#3",
	"E_3",
	"F_3",
	"F#3",
	"G_3",
	"G#3",
	"A_3",
	"A#3",
	"B_3"
]

STEP_SEC = 0.2
WINDOW_SEC = 0.2


SAMPLE_RATE = 16000
WINDOW_SIZE = mylib.ceil_pow(int(WINDOW_SEC * SAMPLE_RATE)) #2048
STEP_SIZE = WINDOW_SIZE #int(STEP_SEC * SAMPLE_RATE)
MAX_FREQ = 1500
MIN_FREQ = 30

HEIGHT = int(MAX_FREQ * WINDOW_SIZE / SAMPLE_RATE)

print("Window size: {} \nStep size: {}".format(WINDOW_SIZE, STEP_SIZE))

def closest_note(freq, value, threshold):
	if freq < MIN_FREQ or freq > MAX_FREQ or value < threshold:
		return "-"
	freq_matrix = np.array(list(NOTES.values()))
	dif = freq_matrix - freq
	dif = np.abs(dif)
	index = np.argmin(dif)
	letter = list(NOTES.keys())
	return letter[index]

def pixel2hz(n, sample_rate=SAMPLE_RATE, window_size=WINDOW_SIZE):
	hzz = {}
	for i in range(n):
		hzz[i] = sample_rate / window_size * i
	return hzz

def play(note, duration, sample_rate):
	size = int(sample_rate * duration)
	s = np.linspace(0, duration, size, endpoint=False)
	if note != "-":
		hz = NOTES[note]
		for i in range(size):
			x = duration / size * i
			s[i] = np.sin(2 * np.pi * hz * x)
	win = 1024
	s[-win:] *= np.hanning(2 * win)[win:]
	return s

def txt2wav(src_file, dst_file, duration):
	music = []
	rate = SAMPLE_RATE
	note_str = ""

	with open(src_file, 'r') as txt_file:
		line = txt_file.readline().strip()
		for note in tqdm(line):
			note_str = note_str + note
			if note == "#" or note == "_" or (note >= "A" and note <= "Z"):
				continue
			music += list(play(note_str, duration, rate))
			note_str = ""

	if dst_file.endswith("wav"):
		librosa.output.write_wav(dst_file, np.array(music), rate)
	if dst_file.endswith("ogg"):
		sf.write(dst_file, np.array(music), rate, format='ogg')
	if dst_file.endswith("opus"):
		wav_file = dst_file + ".wav"
		sf.write(wav_file, np.array(music), rate, format='wav')
		cmd = f"opusenc {wav_file} {dst_file}"
		os.system(cmd)

def wav2txt(src_file, dst_file, threshold=0.2):
	window_size = WINDOW_SIZE
	step_size = STEP_SIZE

	data, rate = librosa.load(src_file, sr=SAMPLE_RATE)
	spectr = mylib.stft(data, window_size, step_size)
	spectr_abs = np.abs(spectr)

	file_name = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	spectr_directory = "img/"
	if not os.path.exists(spectr_directory):
		os.mkdir(spectr_directory)
	spectr_img_path = spectr_directory + file_name + ".pdf"
	plt.figure(figsize=(60, 60))
	plt.imshow(spectr_abs[:HEIGHT,:] ** 0.125)
	plt.savefig(spectr_img_path)

	mel_directory = "mel/"
	if not os.path.exists(mel_directory):
		os.mkdir(mel_directory)
	mel_img_path = mel_directory + file_name + ".pdf"
	plt.figure(figsize=(60, 60))
	mel_spectr = librosa.feature.melspectrogram(
		data, 
		sr=16000,
		n_fft=2048,
		hop_length=512,
		n_mels=100
	)
	plt.imshow(mel_spectr[:HEIGHT,:] ** 0.125)
	plt.savefig(mel_img_path)

	chroma_directory = "chroma/"
	if not os.path.exists(chroma_directory):
		os.mkdir(chroma_directory)
	chroma_img_path = chroma_directory + file_name + ".pdf"
	plt.figure(figsize=(60, 60))
	chroma_spectr = librosa.feature.chroma_stft(
		data, 
		sr=16000,
		n_fft=2048,
		hop_length=512
	)
	plt.figure(figsize=(60, 60))
	plt.imshow(chroma_spectr, origin='top')
	plt.savefig(chroma_img_path)

	table = pixel2hz(spectr.shape[0])
	max_pixel = np.argmax(spectr_abs, axis=0)
	logging.info("Argmax results pixel:\n {}".format(max_pixel))
	freq_table = np.zeros(max_pixel.size)

	for i in range(max_pixel.size):
		freq_table[i] += table[max_pixel[i]]
	logging.info("Argmax results hz:\n {}".format(freq_table))

	max_pixel_value = np.max(spectr_abs, axis=0)
	logging.info("Argmax results value:\n {}".format(max_pixel_value))

	notes_list = []
	abs_threshold = threshold * np.max(max_pixel_value)
	for i in range(freq_table.size):
		note = closest_note(freq_table[i], max_pixel_value[i], abs_threshold)
		notes_list.append(note)

	music = "".join(notes_list)
	with open(dst_file, 'w') as txt_file:
		txt_file.write(music)

	# note_max = np.argmax(chroma_spectr, axis=0)
	# logging.info("Note results hz:\n {}".format(note_max))

	# notes_list = []
	# for i in range(note_max.size):
	# 	notes_list.append(KEYS[note_max[i]])

	# music = "".join(notes_list)
	# with open(dst_file, 'w') as txt_file:
	# 	txt_file.write(music)


def get_args():
	parser = argparse.ArgumentParser(description='Convert wav to music or vice versa')
	parser.add_argument(
		'src_file',
		type=str,
		help='source file'
	)
	parser.add_argument(
		'dst_file',
		type=str,
		help='destination file'
	)
	parser.add_argument(
		'-window',
		type=float,
		help='window'
	)
	parser.add_argument(
		'-threshold',
		type=float,
		help='threshold'
	)
	parser.add_argument(
		'-t',
		'--txt2wav',
		help='wav2txt or txt2wav mode (default: wav2txt)',
		action='store_true'
	)
	return parser.parse_args()

def init_logger():
	file_name = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	log_directory = "log/"
	if not os.path.exists(log_directory):
		os.mkdir(log_directory)
	log_path = log_directory + file_name + ".log"
	# add filemode="w" to overwrite
	logging.basicConfig(filename=log_path, level=logging.INFO, format='\n%(asctime)s\n%(message)s')


def main():
	init_logger()
	args = get_args()
#	print("{}".format(args))
	if args.txt2wav:
		txt2wav(src_file=args.src_file, dst_file=args.dst_file, duration=args.window)
	else:
		wav2txt(src_file=args.src_file, dst_file=args.dst_file, threshold=args.threshold)


if __name__ == "__main__":
	main()
