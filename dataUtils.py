from mido import MidiFile
from theano import tensor
import os, copy, pickle
import numpy as np

DICE = False
if "DICE" in os.environ and os.environ["DICE"] == 1:
	DICE = True

if DICE == False:
	dataset_path = "/Users/Bernat/Dropbox/UoE/Dissertation/midiFiles/"
	test_path = "/Users/Bernat/Dropbox/UoE/Dissertation/testMidi/"

else:
	dataset_path = "/afs/inf.ed.ac.uk/user/s14/s1471922/Dissertation/midiFiles/"
	test_path = "/afs/inf.ed.ac.uk/user/s14/s1471922/Dissertation/testMidi/"



def saveRepresentation(song, fileName):
	with open(test_path + fileName, 'wb') as f:
		pickle.dump(my_list, f)

def loadRepresentation(fileName):
	with open(test_path + fileName, 'rb') as f:
		my_list = pickle.load(f)
		return my_list

def maxTimesteps(limitSongs):
	maxSteps = 0
	for fileName in os.listdir(dataset_path):
		if ".mid" in fileName:
			mid = MidiFile(dataset_path + fileName) 
			numSteps = 0
			for message in mid.tracks[0]:
				numSteps += message.time
			maxSteps = max([maxSteps, numSteps])
			limitSongs -= 1
			if limitSongs == 0:
				break
	return maxSteps

def createRepresentation(limitSongs=0):
	timesteps = maxTimesteps(limitSongs)
	#To Do: if limitSongs is bigger than the actual maximum or is 0 we should look for the number of files in the path to determine the first dimension
	#To Do: extract notes that are triggered so that we can reduce the third dimension from 128 to a smaller value
	songs = np.zeros((limitSongs, timesteps, 128))
	idx = 0
	for fileName in os.listdir(dataset_path): #iterate per file
		if ".mid" in fileName: #check
			print "Loading file %d: %s" % (idx+1, fileName)
			mid = MidiFile(dataset_path + fileName)
			for i, track in enumerate(mid.tracks):
				if i != 0: #track 0 contains meta info we don't need
					ts = 0 #init time
					notesOn = []
					for message in track:
						ticks = message.time #indicates delta change where next event is happening
						while ticks > 0: #advance timestep pointer to delta while we keep enabling the activated notes
							for note in notesOn:
								songs[idx][ts][note-1] = 1
							ticks -= 1
							ts += 1

						#update state at current timestep according to message
						if message.type == 'note_on':
							notesOn.append(message.note)
						if message.type == 'note_off':
							notesOn.remove(message.note) #To do: check if ValueError is triggered

			#check limit of songs for collection
			limitSongs -= 1
			if limitSongs == 0:
				break
			idx += 1 #next song...
			#could merge idx with limitsongs

	return songs

