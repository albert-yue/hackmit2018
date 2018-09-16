# The aim of this file is to take the phoneme_audios pickled data and run our algorithm on it

import random
import numpy as np
import sys
import pickle
import matplotlib.pyplot as plt

with open("phoneme_audios.p", 'rb')as p:
	phoneme_audios = pickle.load(p) # TODO this should be read in somehow
# The structure of this data structure is phoneme to list of audios (each of which is a list)

print(phoneme_audios.keys())
#print(phoneme_audios['M'][0].shape)

num_guesses = 10
min_length = 600
print("Min length: ", min_length)
max_length = 25000
threshold = 10000

def evaluate(candidate_field, phoneme):
	audios = phoneme_audios[phoneme]
	retval = 0
	for audio in audios:
		retval += np.max(np.correlate(candidate_field, audio, "full"))
	retval /= np.sqrt(len(candidate_field))
	print(retval)
	return retval

def good_to_best(field, phoneme):
	#print(field)
	audios = phoneme_audios[phoneme]
	retval = 0
	best = np.zeros(max_length)
	for audio in audios:
		buffered_audio = np.hstack((np.zeros(len(field)), audio, np.zeros(len(field))))
		#print(buffered_audio)
		#print(np.argmax(np.correlate(buffered_audio, field, "full")))
		clipped_overlap = buffered_audio[np.argmax(np.correlate(buffered_audio, field, "full"))-len(field)+1:][:max_length]
		#print(clipped_overlap)
		to_add = clipped_overlap
		if len(clipped_overlap) < max_length:
			to_add = np.hstack((clipped_overlap, np.zeros(max_length-len(clipped_overlap))))
		#print(to_add)
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
	print(last)
	return field[:last+1]

phoneme_dict = {}
for phoneme in phoneme_audios:
	# phoneme = 'NG'
	audios = phoneme_audios[phoneme]
	fields = []
	field_evals = []
	for i in range(num_guesses):
		indices = random.sample(range(len(audios)), 2)
		first = audios[indices[0]]
		second = audios[indices[1]]
		#print(first.shape, second.shape)
		# #print(np.correlate(first, second, "full"))
		position = np.argmax(np.correlate(first, second, "full"))

		first_start = max(0, position-len(second)+1)
		first_end = min(position, len(first)-1) - min_length + 1
		second_start = max(0, len(second)-1 - position)
		second_end = len(second)-1 - max((position-len(first)+1),  0) - min_length+1
		#print(first_start, first_end, second_start, second_end)
		#print((first_end-first_start) == (second_end-second_start)) # Should be true always
		num_positions = first_end-first_start+1
		if (num_positions < 0):
			print("ERROR 1!")
			continue
		dot_products = np.zeros(num_positions)
		for j in range(num_positions):
			dot_products[j] = np.dot(first[first_start+j:first_start+j+min_length], second[second_start+j:second_start+j+min_length])
		#print(dot_products)
		print(np.max(dot_products))
		print(np.sort(dot_products)[-100:-90])
		thresholded_dots = np.where(dot_products > threshold, 1, 0)
		print(np.sum(thresholded_dots))
		bounded = np.hstack(([0], thresholded_dots, [0]))
		# get 1 at run starts and -1 at run ends
		difs = np.diff(bounded)
		# #print(difs)
		run_starts, = np.where(difs > 0)
		run_ends, = np.where(difs < 0)
		# #print(run_starts, run_ends)
		temp_ind = np.argmax(run_ends - run_starts)
		start = run_starts[temp_ind]
		end = run_ends[temp_ind]
		first_field = first[first_start+start:first_start+end-1+min_length]
		second_field = second[second_start+start:second_start+end-1+min_length]
		#print(first_field, second_field)
		print(len(first_field), len(second_field))
		receptive_field = np.add(first_field, second_field)/2

		fields.append(receptive_field)
		field_evals.append(evaluate(receptive_field, phoneme))
	best_guess_ind = np.argmax(np.array(field_evals))
	good_guess = fields[best_guess_ind]
	best_guess = good_to_best(good_guess, phoneme)
	phoneme_dict[phoneme] = trim_best(best_guess, 500, 2000) # TODO: Tune these last two parameters
evaluate(phoneme_dict[phoneme], phoneme)
# plt.subplot(211)
# plt.plot(first)
# plt.subplot(212)
# plt.plot(best_guess)
# # plt.plot(second)
# plt.show()

pickle.dump(phoneme_dict, open('phoneme_dict.p', 'wb'))

		

