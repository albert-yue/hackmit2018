import pickle as pkl

# We read in 

print("This program lets you make NAME HERE pronounce anything!")

again = 'y'

while (again.lower() == 'y'):
	input_text = input("Enter text you want to generate speech for: ")

	generate_audio_out(input_text)

	again = input("Audio generated! Generate more? (Y/N): ")

# For this method, we want to split the input text
def generate_audio_out(input_text):
	pass
