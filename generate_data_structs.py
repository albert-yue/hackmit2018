import requests
import time
import pronouncing
import pickle
from scipy.io import wavfile
from itertools import chain
import numpy as np

# We use this file to generate our data structures
# For every new audio file, this file should be run once
# As input, this file will take an audio file (specified via f)
# As output, this file will generate pickle files for two variables:
#		punctuation_lengths - A dictionary mapping different punctuation to average length (in seconds) of the pause
#		phoneme_audios - A dictionary mapping phonemes to lists of audio clips of words containing the phoneme

filepath = 'media/ndt1.wav'
rev_api_key = open("rev_api_key.txt", "r").read()

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
def create_rev_job(filepath, headers):
    # Code adapted from https://github.com/amikofalvy/revai-python-example/blob/master/example.py
    url = 'https://api.rev.ai/revspeech/v1beta/jobs'
    files = { 'media': (filepath, open(filepath, 'rb'), 'audio/wav') }
    
    request = requests.post(url, headers=headers, files=files)

    response_body = request.json()
    return response_body['id']

def view_job(job_id, headers):
    # Code adapted from https://github.com/amikofalvy/revai-python-example/blob/master/example.py
    url = f'https://api.rev.ai/revspeech/v1beta/jobs/{job_id}'
    request = requests.get(url, headers=headers)

    return request.json()

def get_transcript(job_id, headers):
    # Code adapted from https://github.com/amikofalvy/revai-python-example/blob/master/example.py
    url = f'https://api.rev.ai/revspeech/v1beta/jobs/{job_id}/transcript'

    headers['Accept'] = 'application/vnd.rev.transcript.v1.0+json'
    request = requests.get(url, headers=headers)

    return request.json()

def get_rev_results(filepath):    
    """ Create the rev job. """
    headers = {'Authorization': f"Bearer {rev_api_key}"}
    
    transcript_id = create_rev_job(filepath, headers)

    status = 'in_progress'
    response = ''

    while status == 'in_progress':
        response = view_job(transcript_id, headers)
        status = response['status']

    return flatten([monologue['elements'] for monologue in get_transcript(transcript_id, headers)['monologues']])

def flatten(list_of_lists):
    # from https://docs.python.org/3/library/itertools.html#recipes
    return list(chain.from_iterable(list_of_lists))

# Step 2: Read in audio file and create {word: [list of audio clips]} dictionary using REV results - call this word_audios
#			We should also create another dictionary {punct: length} - call this punctuation_lengths and pickle it
# Basically, we should iterate through the REV elements for speaker 1 and do the appropriate processing. Note for
# 		length of punctuation, we'll need to approximate by taking the difference between the start of the next word
#		and the end of the previous word. This is also how we will approach spaces.
# Another thing to note is that we may want to discard words predicted with <50% confidence or something as that's
#		probably not accurate
def process_transcript(rev_results, filepath):
    fs, data = wavfile.read(filepath)
    sampling_rate = 44100
    word_dict = {}
    punct_dict = {}
    punct_lengths = {}

    for i in range(len(rev_results)):
        # Handle punctuation.
        if rev_results[i]['type'] == 'punct':
            value = rev_results[i]['value']
            if i == 0 or  i == len(rev_results) - 1:
                continue
            duration = rev_results[i+1]['ts'] - rev_results[i-1]['end_ts']

            if value not in punct_lengths:
                punct_lengths[value] = []
            
            punct_lengths[value].append(duration)

            continue

        # Handle words.
        if rev_results[i]['type'] != 'text' or rev_results[i]['confidence'] < 0.5:
            continue
        
        word = rev_results[i]['value']
        start_index = int(sampling_rate * rev_results[i]['ts'])
        end_index = int(sampling_rate * rev_results[i]['end_ts'])

        if word not in word_dict:
            word_dict[word] = []

        audio_clip = [0]*(end_index-start_index)
        for i in range(end_index-start_index):
            audio_clip[i] = data[start_index+i][0]
        word_dict[word].append(np.array(audio_clip))

    for key, value in punct_lengths.items():
        punct_dict[key] = sum(punct_lengths[key])/len(punct_lengths[key])

    return punct_dict, word_dict



# Step 3: Make dictionary of phonemes (aka our internal representation of phonemes) to words - call this phoneme_words
# Here, we need to iterate through the keys of the previous dictionary (aka all the words) and find the phonemes present
#		in them (perhaps by pinging a website using the requests module?). Other than that, this should be quite simple;
#		just add a newly discovered phoneme to the dictionary, otherwise append the word to the relevant value lists.
#		Might be useful to use python's setdefault method just for shorter code XD
def get_phonemes_to_words(words):
    phonemes_to_words = {}

    unique_words = set(words)

    for word in unique_words:
    	phonemes = phonemes_for(word)

    	if phonemes is None:
    		continue

    	for phoneme in phonemes:
    		if phoneme not in phonemes_to_words:
    			phonemes_to_words[phoneme] = set()
    		phonemes_to_words[phoneme].add(word)

    return phonemes_to_words

def phonemes_for(word):
	translated = pronouncing.phones_for_word(word)
	if len(translated) == 0:
		return None
	return translated[0].split(" ")

# Step 4: Make dictionary of phonemes (aka our internal representation of phonemes) to audio clips - call this phoneme_audios and pickle it
# For this step, we simply iterate through all the keys of phoneme_words. For each key, we iterate through the words in the
#		value list and for each one we get its list of audioclips (from word_audios), then we concatenate all these lists
#		of audio clips.
def get_phoneme_audios(word_dict, phonemes_to_words):
    phoneme_audios = {}

    for phoneme, words in phonemes_to_words.items():
        all_clips = []
        for word in words:
            for clip in word_dict[word]:
                all_clips.append(clip)
        
        phoneme_audios[phoneme] = all_clips
    
    return phoneme_audios

if __name__ == '__main__':
    rev_results = get_rev_results(filepath)
    punct_dict, word_dict = process_transcript(rev_results, filepath)

    phonemes_to_words = get_phonemes_to_words(word_dict.keys())

    phoneme_audios = get_phoneme_audios(word_dict, phonemes_to_words)

    pickle.dump(phoneme_audios, open('phoneme_audios.p', 'wb'))


