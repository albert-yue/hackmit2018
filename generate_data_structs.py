# We use this file to generate our data structures
# For every new audio file, this file should be run once
# As input, this file will take an audio file (specified via f)
# As output, this file will generate pickle files for two variables:
#		punctuation_lengths - A dictionary mapping different punctuation to average length (in seconds) of the pause
#		phoneme_audios - A dictionary mapping phonemes to lists of audio clips of words containing the phoneme

filename = ''

# TODO: we need to have some internal representation of phonemes (maybe just number them). I feel that just "spelling"
#		them out is not the best idea.

# Step 1: Send audio file to REV api and get results - call them rev_results
# Example result: 
# {
#   "monologues": [
#     {
#       "speaker": 1,
#       "elements": [
#         {
#           "type": "text",
#           "value": "Hello",
#           "ts": 0.5,
#           "end_ts": 1.5,
#           "confidence": 0.99
#         },
#         {
#           "type": "punct",
#           "value": "."
#         }
#       ]
#     }
#   ]
# }
# TODO: See how this gets read into python


# Step 2: Read in audio file and create {word: [list of audio clips]} dictionary using REV results - call this word_audios
#			We should also create another dictionary {punct: length} - call this punctuation_lengths and pickle it
# Basically, we should iterate through the REV elements for speaker 1 and do the appropriate processing. Note for
# 		length of punctuation, we'll need to approximate by taking the difference between the start of the next word
#		and the end of the previous word. This is also how we will approach spaces.
# Another thing to note is that we may want to discard words predicted with <50% confidence or something as that's
#		probably not accurate


# Step 3: Make dictionary of phonemes (aka our internal representation of phonemes) to words - call this phoneme_words
# Here, we need to iterate through the keys of the previous dictionary (aka all the words) and find the phonemes present
#		in them (perhaps by pinging a website using the requests module?). Other than that, this should be quite simple;
#		just add a newly discovered phoneme to the dictionary, otherwise append the word to the relevant value lists.
#		Might be useful to use python's setdefault method just for shorter code XD

# Step 4: Make dictionary of phonemes (aka our internal representation of phonemes) to audio clips - call this phoneme_audios and pickle it
# For this step, we simply iterate through all the keys of phoneme_words. For each key, we iterate through the words in the
#		value list and for each one we get its list of audioclips (from word_audios), then we concatenate all these lists
#		of audio clips.
