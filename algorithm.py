# The aim of this file is to take the phoneme_audios pickled data and run our algorithm on it

import random
import numpy as np
import pickle

with open("phoneme_audios.p", 'rb')as p:
	phoneme_audios = pickle.load(p) # TODO this should be read in somehow
# The structure of this data structure is phoneme to list of audios (each of which is a list)

num_guesses = 1
min_length = 2
max_length = 10
threshold = 7

def evaluate(candidate_field, phoneme):
	audios = phoneme_audios[phoneme]
	retval = 0
	for audio in audios:
		retval += np.max(np.correlate(candidate_field, audio, "full"))
	print(retval)
	return retval

def good_to_best(field, phoneme):
	print(field)
	audios = phoneme_audios[phoneme]
	retval = 0
	best = np.zeros(max_length)
	for audio in audios:
		buffered_audio = np.hstack((np.zeros(len(field)), audio, np.zeros(len(field))))
		print(buffered_audio)
		print(np.argmax(np.correlate(buffered_audio, field, "full")))
		clipped_overlap = buffered_audio[np.argmax(np.correlate(buffered_audio, field, "full"))-len(field)+1:][:max_length]
		print(clipped_overlap)
		to_add = clipped_overlap
		if len(clipped_overlap) < max_length:
			to_add = np.hstack((clipped_overlap, np.zeros(max_length-len(clipped_overlap))))
		print(to_add)
		best = np.add(best, to_add)
	return best/len(audios)

def trim_best(field, thresh, num):
	current = 0
	last = max_length
	for i in range(len(field)):
		val = field[i]
		if (abs(val) > thresh):
			last = i
			current = 0
		else:
			current += 1
		if current >= num:
			break
	return field[:last+1]

phoneme_dict = {}
for phoneme in phoneme_audios:
	audios = phoneme_audios[phoneme]
	fields = []
	field_evals = []
	for i in range(num_guesses):
		indices = random.sample(range(len(audios)), 2)
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
	best_guess_ind = np.argmax(np.array(field_evals))
	good_guess = fields[best_guess_ind]
	phoneme_dict[phoneme] = trim_best(good_to_best(good_guess, phoneme), 1, 2) # TODO: Tune these last two parameters

pickle.dump(phoneme_dict, open('phoneme_dict.p', 'wb'))

		

