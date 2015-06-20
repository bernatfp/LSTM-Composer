from mido import MidiFile
from theano import tensor
import os, copy, pickle


DICE = False
if "DICE" in os.environ and os.environ["DICE"] == 1:
	DICE = True

if DICE == False:
	path = "/Users/Bernat/Dropbox/UoE/Dissertation/midiFiles/"
else
	path = "/afs/inf.ed.ac.uk/user/s14/s1471922/Dissertation/MidiFiles/"






def saveRepresentation(song, fileName):
	with open(path + fileName, 'wb') as f:
		pickle.dump(my_list, f)

def loadRepresentation(fileName):
	with open(path + fileName, 'rb') as f:
		my_list = pickle.load(f)
		return my_list

def createRepresentation():
	#newTimestep = [0] * 128 #initial representation of a timestep on a song
	seqNumSteps = [] #array of number of timesteps per song
	songs = [] #collection of representations
	for fileName in os.listdir(path): #iterate per file
		song = [] #representation of this midi file
		numSteps = 0 #number of steps that this midi file has
		if ".mid" in fileName: #check
			mid = MidiFile(path + fileName) 
			for i, track in enumerate(mid.tracks):
				if i == 0: #first track contains meta-messages only
					for message in track:
						numSteps += message.time
					
					seqNumSteps.append(numSteps) #add 1 to avoid getting out of bounds
					#song = [newTimestep] * (numSteps) #allocate memory needed to store song
					for i in xrange(numSteps+1):
						song.append([0]*128)
							
					if numSteps == 0:
						print "Error, info about time missing."
						return
					print "File: %s    Number of steps: %d" % (fileName, numSteps)
				else: #other tracks contain the actual music
					timestep = 0 #init time
					notesOn = []
					for message in track:
						#ticks = message.time #indicates delta change where next event is happening
						ticks = message.time #indicates delta change where next event is happening
						print "Current timestep: %d    Number of ticks next event: %d" % (timestep, ticks)
						print "Limit steps: %d     Current timestep + ticks next event: %d" % (numSteps, timestep+ticks)
						while ticks > 0: #advance timestep pointer to delta while we keep enabling the activated notes
							for note in notesOn:
								song[timestep][note-1] = 1
							ticks -= 1
							timestep += 1

						#update state at current timestep according to message
						if message.type == 'note_on':
							notesOn.append(message.note)
							#song[timestep][message.note-1] = 1
						if message.type == 'note_off':
							notesOn.remove(message.note) #check if ValueError is triggered
							#song[timestep][message.note-1] = 0


			#print song
			#x = raw_input("Wait...")
			songs.append(song)
	return songs

