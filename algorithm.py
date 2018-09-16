# The aim of this file is to take the phoneme_audios pickled data and run our algorithm on it

import random from random

phoneme_audios = {} # TODO this should be read in somehow
# The structure of this data structure is phoneme to list of audios (each of which is a list)

num_guesses = 100

for phoneme in phoneme_audios:
	audios = phoneme_audios[phoneme]
	for i in range(num_guesses):
		clips = random.sample(audios, 2)