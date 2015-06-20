from mido import MidiFile
import os, copy


import timeit
import operator #for sorting dict

path = "/Users/Bernat/Dropbox/UoE/Dissertation/midiFiles/"

def eventsSong(fileName):
	times = []
	mid = MidiFile(path + fileName)
	for i, track in enumerate(mid.tracks):
		time = 0
		print('Track {}: {}'.format(i, track.name))
		for message in track:
			print message
			time += message.time
		times.append(time)
	return times


def printInfo():
	minticks = 10000000
	minnote = 1000
	maxnote = -1
	ticksdict = {}
	for fileName in os.listdir(path):
		if ".mid" in fileName:
			mid = MidiFile(path + fileName)
			#print "Name: " + fileName  
			#print "Type: %d" % (mid.type)
			for i, track in enumerate(mid.tracks):
				#if i > 0: #to only print meta info about track
				#	break
				#print('Track {}: {}'.format(i, track.name))
				count = 0
				for message in track:
					#if message.type == 'note_on':
					#	minnote = min([minnote, message.note])
					#	maxnote = max([maxnote, message.note])
					#	print maxnote, minnote
					#print message
					#count += 1
					#if count > 20:
					#	break
					#
					if message.type == 'note_off':
						ticks = message.time
						if ticks > 0:	
							if ticks not in ticksdict:
								ticksdict[ticks] = 1
							else:
								ticksdict[ticks] += 1

					#if ticks % 1024 != 0:
					#	print "Number of ticks not divisible by 1024: %d" % (ticks)
					#	print "%d / 1024 = %d      %d mod 1024 = %d" % (ticks, ticks/1024, ticks, ticks%1024)
	
	sorted_x = sorted(ticksdict.items(), key=operator.itemgetter(1)) #sort by val
	print sorted_x
	sorted_x = sorted(ticksdict.items(), key=operator.itemgetter(0)) #sort by key
	print sorted_x



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

#printInfo()
print "Start"
print timeit.timeit('createRepresentation()', setup='from __main__ import createRepresentation', number=1)
print "Stop"







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








timestep = 0 #init time 
for message in track:
	#ticks = message.time #indicates delta change where next event is happening
	ticks = message.time #indicates delta change where next event is happening
	print "Current timestep: %d    Number of ticks next event: %d" % (timestep, ticks)
	print "Limit steps: %d     Current timestep + ticks next event: %d" % (numSteps, timestep+ticks)
	while ticks > 0: #advance timestep pointer to delta with copys of past state (need to avoid referencing)
		ticks -= 1
		timestep += 1
		song[timestep] = copy.copy(song[timestep-1]) #because we always copy - 1 we have allocated an extra step before
	#update state at current timestep according to message
	if message.type == 'note_on':
		song[timestep][message.note-1] = 1
	if message.type == 'note_off':
		song[timestep][message.note-1] = 0


