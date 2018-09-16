import numpy as np
import pickle
import re
from generate_data_structs import phonemes_for

# We read in 

print("This program lets you make NAME HERE pronounce anything!")

clip = pickle.load(open("phoneme_dict.p", "rb"))
again = 'y'

while (again.lower() == 'y'):
	input_text = input("Enter text you want to generate speech for: ")

	generate_audio_out(input_text)

	again = input("Audio generated! Generate more? (Y/N): ")

# For this method, we want to split the input text
def ispunc(word):
	for char in word:
		if char.isalnum():
			return False
	return True

def generate_audio_out(input_text):
	words = re.findall(r"[\w']+|[.,!?;]", input_text)
	clips = []

	for word in words:
		if not ispunc(word):
			clips.append(generate_audio_for_word(word))
		clips.append(np.zeros(10))
	return stitch_audio(clips)

def generate_audio_for_word(word):
	# get the phonemes
	phonemes = phonemes_for(word)
	# convert each phoneme to audio clip
	audio_clips = [clip[pho] for pho in phonemes]
	# stitch together and return
	return stitch_audio(audio_clips)

def stitch_audio(audio_clips):
	"""
	Stitches together a list of audio clips, each of which is a numpy array of waveform values

	Implementation: naively concatenate together the clips
	"""
	np.concatenate(audio_clips)
