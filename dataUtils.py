from mido import Message, MidiFile, MidiTrack
import matplotlib.pyplot as plt
import os, copy, pickle
import numpy as np
import time


def saveData(data, dataDir):
	with open(dataDir, 'wb') as f:
		pickle.dump(data, f)

def loadData(dataDir):
	with open(dataDir, 'rb') as f:
		data = pickle.load(f)
		return data


def maxTimesteps(limitSongs):
	maxSteps = 0
	for fileName in sorted(os.listdir(dataset_path)):
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

def getTimesteps(dataDir, limitSongs):
	timesteps = []
	for fileName in sorted(os.listdir(dataDir)):
		if ".mid" in fileName:
			mid = MidiFile(dataDir + fileName) 
			numSteps = 0
			for message in mid.tracks[0]:
				numSteps += message.time
			timesteps.append(numSteps)
			limitSongs -= 1
			if limitSongs == 0:
				break
	return timesteps


#This function loads the .mid files and converts them to a reduced (in the time axis) piano roll representation
def createRepresentation(dataDir, limitSongs=0, reductionRatio=128):
	#perhaps it would make more sense to create a midi2roll function aside and simplify this one
	#To Do: if limitSongs is bigger than the actual maximum or is 0 we should look for the number of files in the path to determine the first dimension
	#To Do: extract notes that are triggered so that we can reduce the third dimension from 128 to a smaller value

	#timesteps = maxTimesteps(limitSongs)
	#songs = np.zeros((limitSongs, timesteps, 128))
	timesteps = getTimesteps(dataDir, limitSongs)
	songs = []
	idx = 0
	for fileName in sorted(os.listdir(dataDir)): #iterate per file
		if ".mid" in fileName: #check
			print "Loading file %d: %s" % (idx+1, fileName)
			mid = MidiFile(dataDir + fileName)
			song = np.zeros(np.array((np.ceil(1+timesteps[idx]/float(reductionRatio)), 128+1))) #1 additional note to denote end of track
			for i, track in enumerate(mid.tracks):
				if i != 0: #track 0 contains meta info we don't need
					ts = 0 #init time
					realts = 0
					notesOn = []
					for message in track:
						ticks = message.time #indicates delta change where next event is happening
						while ticks > 0: #advance timestep pointer to delta while we keep enabling the activated notes
							for note in notesOn:
								#songs[idx][ts][note-1] = 1
								song[ts][note] = 1
							ticks -= 1
							realts += 1
							if np.floor(realts/float(reductionRatio)) > ts:
								ts += 1

						#update state at current timestep according to message
						if message.type == 'note_on':
							notesOn.append(message.note)
						if message.type == 'note_off':
							notesOn.remove(message.note) #To do: check if ValueError is triggered

			#denote end of track
			song[-1][-1] = 1
			#add to songs
			songs.append(song)

			#check limit of songs for collection
			limitSongs -= 1
			if limitSongs == 0:
				break
			idx += 1 #next song...
			#could merge idx with limitsongs

	return songs

def thresholdOutput(x, threshold=0.5, normalize=False):
	return [0 if note < threshold else 1 for note in x]

def sampleOutput(x, normalize=False):
	if normalize:
		return [0 if np.random.uniform() > normalizeProbability(note) else 1 for note in x]
	else:
		return [0 if np.random.uniform() > note else 1 for note in x]

def normalizeProbability(prob):
	return 1/(1+np.power(10000, (-prob + 0.5)))

def roll2midi(roll, notesMap, reductionRatio=128): #roll is a (1, ts, input_dim) tensor
	mid = MidiFile()

	track = MidiTrack()
	mid.tracks.append(track)

	tones = np.zeros(roll.shape[1])
	ticks = 0
	for ts in roll:
		for i in range(ts.shape[0]-1):

			if ts[i] == 1 and tones[i] == 0:
				#record note_on event
				track.append(Message('note_on', velocity=127, note=notesMap[i], time=ticks*reductionRatio))
				tones[i] = 1
				ticks = 0

			if ts[i] == 0 and tones[i] == 1:
				#record note_off event
				track.append(Message('note_off', velocity=127, note=notesMap[i], time=ticks*reductionRatio))
				tones[i] = 0
				ticks = 0

		ticks += 1

	#last pass for notes off (end of track)	
	for i in range(roll.shape[1]):
		if tones[i] == 1:
			track.append(Message('note_off', note=notesMap[i], time=ticks*reductionRatio))
			ticks = 0

	return mid

def saveMidi(mid, path):
	mid.save("%ssong.mid" % (path))

#This function removes unnecessary notes and returns mapping of indexes to notes
def compressInputs(X, Y, notesMap=None):
	notesDel = set(range(129))
	for i in range(X.shape[0]):
		print i
		for j in range(X.shape[1]):
			for k in range(X.shape[2]):
				if X[i][j][k] == 1 and k in notesDel:
					notesDel.remove(k)

	#Just in case Y is not contained within X (depends on previous processing of roll to create inputs)
	for i in range(Y.shape[0]):
		for k in range(Y.shape[1]):
			if Y[i][k] == 1 and k in notesDel:
				notesDel.remove(k)

	if notesMap is not None:
		notesDel = notesDel.difference(set(notesMap))
		
	X = np.delete(X, list(notesDel), 2)
	Y = np.delete(Y, list(notesDel), 1)


	notesMap = set(range(129)).difference(notesDel)

	return X, Y, sorted(list(notesMap))


#This function creates samples out of each song
def createModelInputs(roll, seqLength=50, inc=1, padding=False):
	#roll is a list of numpy.array
	#split into arbitrary lenght sequences and extract next tone for a sequence (Y)
	#To do (idea): split into shorter melodies cutting any empty part that is long enough.
	X = []
	Y = []
	maxlength = max([len(s) for s in roll])-1
	minlength = min([len(s) for s in roll])-1
	for song in roll:
		#start (padding + seq)
		if padding == True:
			pos = 0
			empty = np.zeros((seqLength,128+1))
			while (pos < seqLength and pos < song.shape[0]):
				#zeros + part of seq
				sample = np.concatenate((empty[pos:],song[:pos]))
				X.append(sample)
				Y.append(song[pos])
				pos += inc

			#if seqLength is larger than song length
			if pos >= song.shape[0]:
				continue

		#mid
		pos = 0
		while pos+seqLength < song.shape[0]:
			sample = np.array(song[pos:pos+seqLength])
			X.append(sample)
			Y.append(song[pos+seqLength])
			pos += inc

		#don't implement end (seq + padding) because that could encourage stopping


	return np.array(X), np.array(Y)


def countDifferentTones(song):
	if len(song.shape) == 3 and song.shape[0] == 1:
		song = song[0]
	tones = 0
	for i in xrange(len(song)-1):
		if np.sum(song[i]-song[i+1]) > 0:
			tones += 1
	return tones

def expandInputs(songs, notesMap):
	songsList = []
	for i in xrange(len(songs)):
		song = np.zeros((songs[i].shape[0],128))
		for j in xrange(songs[i].shape[0]):
			for k in xrange(len(notesMap)):
				song[j][notesMap[k]] = songs[i][j][k]
		songsList.append(song)

def plotSong(song):
	plt.matshow(np.transpose(song))
	plt.colorbar()
	plt.show()

def plot2Songs(s1, s2):
	f, (ax1, ax2) = plt.subplots(2)
	m1 = ax1.matshow(np.transpose(s1))
	#ax1.set_title('Original song')
	ax2.matshow(np.transpose(s2))
	#ax2.set_title('Probabilities at middle layer')
	# Fine-tune figure; make subplots close to each other and hide x ticks for
	# all but bottom plot.
	f.subplots_adjust(right=0.8)
	cbar_ax = f.add_axes([0.85, 0.15, 0.05, 0.7])
	f.colorbar(m1,cax=cbar_ax)
	#plt.setp([a.get_xticklabels() for a in f.axes[:-1]], visible=False)
	plt.show()



def plot3Songs(s1, s2, s3):
	f, (ax1, ax2, ax3) = plt.subplots(3)
	m1 = ax1.matshow(np.transpose(s1))
	#ax1.set_title('Original song')
	ax2.matshow(np.transpose(s2))
	#ax2.set_title('Probabilities at middle layer')
	ax3.matshow(np.transpose(s3))
	#ax3.set_title('Output song')
	# Fine-tune figure; make subplots close to each other and hide x ticks for
	# all but bottom plot.
	f.subplots_adjust(right=0.8)
	cbar_ax = f.add_axes([0.85, 0.15, 0.05, 0.7])
	f.colorbar(m1,cax=cbar_ax)
	#plt.setp([a.get_xticklabels() for a in f.axes[:-1]], visible=False)
	plt.show()

def plotMK(mkmat):

	mat = np.zeros((mkmat.shape[1]*2, mkmat.shape[2]*2))
	mat[:mkmat.shape[1], :mkmat.shape[2]] = mkmat[0]
	mat[mkmat.shape[1]:, mkmat.shape[2]:] = mkmat[1]
	mat[:mkmat.shape[1], mkmat.shape[2]:] = mkmat[2]
	mat[mkmat.shape[1]:, :mkmat.shape[2]] = np.transpose(mkmat[2])

	plt.matshow(mat)
	plt.colorbar()
	plt.show()


