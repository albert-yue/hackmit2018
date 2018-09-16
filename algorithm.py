# The aim of this file is to take the phoneme_audios pickled data and run our algorithm on it

import numpy as np

phoneme_audios = {} # TODO this should be read in somehow
# The structure of this data structure is phoneme to list of audios (each of which is a list)

num_guesses = 100
min_length = 100

for phoneme in phoneme_audios:
	audios = phoneme_audios[phoneme]
	for i in range(num_guesses):
		indices = np.random.randint(audios.shape[0], 2)
		first = audios[indices[0]]
		second = audios[indices[1]]
		position = np.argmax(np.correlate(first, second, "full"))

		first_start = max(0, position-second.size+1)
		first_end = min(position, first.size-1) - min_length + 1
		second_start = max(0, second.size-1 - position)
		second_end = second.size-1 - max((position-first.size+1),  0) - min_length+1