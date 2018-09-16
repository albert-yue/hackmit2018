# hackmit2018

Text-to-speech generation to emulate a voice.

Generate a (clever) guess of for audio to phoneme sound and auto-correlate it with each of the words

Data structures:
1. Run speech to text and use timestamps  to generate  dictionary of words to  audio clips - Specific structure should be {word:  [list of audio]}
2. Take set of words and process to phonemes. Construct dictionary of phonemes to words - Specific structure should be {phoneme: [list of words]}
3. Run through all phonemes. For each phoneme concatenate  all audio lists from each word  in list  of  words. Save as dictionary from phoneme to audios {phoneme:  [list of audio]}
4. Generate audio for each phoneme  via COMPLICATED ALGORITHM and save  as {phoneme: audio clip}

Algorithm:
Input text -> split into words -> split into phonemes -> Use dictionary 4 to get audio clips  per phoneme -> Stitch audios together  to form words -> add small pauses between words and output audio!

Pauses:
For all punctuation/spaces/things that involve pauses, get all speech to text results and  average lengths to generate length of pauses. Save  as dictionary {punctionation: length of  pause}



COMPLICATED ALGORITHM:

Algorithm has two  portions… First  portion is getting to a  decent/good guess. Second portion relies on  a  relatively good  guess, and then generates the best guess.

Pick N  (maybe 100) pairs of audios. Run autocorrelations and find indices of max overlap. Align  audio clips at max overlap and sample correlation for smaller length M segments within. Note that M should be less than the minimum  length of phoneme audio. Only keep segments of length M with a “dot product” above certain threshold T. If segments overlap, combine into a longer audio. We now have 100 potential phoneme audios
We now run each of these against all audios for the phoneme we’re searching for. On each autocorrelation, save the index of max overlap and also determine magnitude. Sum magnitudes across words. Compare this sum across the 100 potential receptive phoneme audios and pick the phoneme audio that maximizes this sum.
For this phoneme audio, make shifts in word audios so the phoneme placement overlaps and average all shifted words. This should generate a long audio containing our phoneme audio surrounded by noise. Find the phoneme in this (again maybe using some threshold), and now we have our best phoneme!