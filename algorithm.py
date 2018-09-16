# The aim of this file is to take the phoneme_audios pickled data and run our algorithm on it

import random
import numpy as np

phoneme_audios = {"test": np.array([list(range(10)), [1, 2, -1, 3, 4, -2, 1]])} # TODO this should be read in somehow
# The structure of this data structure is phoneme to list of audios (each of which is a list)

def evaluate(candidate_field, phoneme):
	audios = phoneme_audios[phoneme]
	retval = 0
	for audio in audios:
		retval += np.max(np.correlate(candidate_field, audio, "full"))
	print(retval)
	return retval

num_guesses = 1
min_length = 2
threshold = 7

for phoneme in phoneme_audios:
	audios = phoneme_audios[phoneme]
	fields = []
	field_evals = []
	for i in range(num_guesses):
		indices = random.sample(range(audios.shape[0]), 2)
		first = audios[indices[0]]
		second = audios[indices[1]]
		print(np.correlate(first, second, "full"))
		position = np.argmax(np.correlate(first, second, "full"))

		first_start = max(0, position-len(second)+1)
		first_end = min(position, len(first)-1) - min_length + 1
		second_start = max(0, len(second)-1 - position)
		second_end = len(second)-1 - max((position-len(first)+1),  0) - min_length+1
		print(first_start, first_end, second_start, second_end)
		print((first_end-first_start) == (second_end-second_start)) # Should be true always
		num_positions = first_end-first_start+1
		if (num_positions < 0):
			print("ERROR 1!")
		dot_products = np.zeros(num_positions)
		for j in range(num_positions):
			dot_products[j] = np.dot(first[first_start+j:first_start+j+min_length], second[second_start+j:second_start+j+min_length])
		print(dot_products)
		thresholded_dots = np.where(dot_products > threshold, 1, 0)
		bounded = np.hstack(([0], thresholded_dots, [0]))
		# get 1 at run starts and -1 at run ends
		difs = np.diff(bounded)
		print(difs)
		run_starts, = np.where(difs > 0)
		run_ends, = np.where(difs < 0)
		print(run_starts, run_ends)
		temp_ind = np.argmax(run_ends - run_starts)
		start = run_starts[temp_ind]
		end = run_ends[temp_ind]
		first_field = first[first_start+start:first_start+end-1+min_length]
		second_field = second[second_start+start:second_start+end-1+min_length]
		print(first_field, second_field)
		receptive_field = np.add(first_field, second_field)/2

		fields.append(receptive_field)
		evaluate(receptive_field, phoneme)
		field_evals.append(evaluate(receptive_field, phoneme))
		

