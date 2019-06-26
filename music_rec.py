import argparse
import librosa
import my_ft_lib as mylib
import numpy as np

NOTES = {
	"D_3" : 146.83,
	"C_4" : 261.63,
	"C#4" : 277.18,
	"D_4" : 293.66,
	"D#4" : 311.13,
	"E_4" : 329.63,
	"F_4" : 349.23,
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
	"B_5" : 987.77,
	"C_6" : 1046.50,
	"C#6" : 1108.73,
	"D_6" : 1174.66,
	"D#6" : 1244.51,
	"E_6" : 1318.51
}

DURATION = 0.2
SAMPLE_RATE = 22050
WINDOW_SIZE = 2048
STEP_SIZE = int(DURATION * SAMPLE_RATE)

def closest_note(freq):
	if freq < 146:
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
	return s

def txt2wav(src_file, dst_file):
	music = []
	rate = SAMPLE_RATE
	duration = DURATION
	note_str = ""

	with open(src_file, 'r') as txt_file:
		for line in txt_file:
			for note in line:
				note_str = note_str + note
				if note == "#" or note == "_" or (note >= "A" and note <= "Z"):
					continue
				music += list(play(note_str, duration, rate))
				note_str = ""

	librosa.output.write_wav(dst_file, np.array(music), rate)

def wav2txt(src_file, dst_file):
	window_size = WINDOW_SIZE
	step_size = STEP_SIZE

	data, rate = librosa.load(src_file)
	spectr = mylib.stft(data, window_size, step_size)
	spectr_abs = np.abs(spectr)
	table = pixel2hz(spectr.shape[0])
	max_pixel = np.argmax(spectr_abs, axis=0)
	freq_table = np.zeros(max_pixel.size)

	for i in range(max_pixel.size):
		freq_table[i] += table[max_pixel[i]]

	notes_list = []
	for i in range(freq_table.size):
		note = closest_note(freq_table[i])
		notes_list.append(note)

	music = "".join(notes_list)
	with open(dst_file, 'w') as txt_file:
		txt_file.write(music)


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
		'-t',
		'--txt2wav',
		help='wav2txt or txt2wav mode (default: wav2txt)',
		action='store_true'
	)
	return parser.parse_args()


def main():
	args = get_args()
#	print("{}".format(args))
	if args.txt2wav:
		txt2wav(src_file=args.src_file, dst_file=args.dst_file)
	else:
		wav2txt(src_file=args.src_file, dst_file=args.dst_file)


if __name__ == "__main__":
	main()
