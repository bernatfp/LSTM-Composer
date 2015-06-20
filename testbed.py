from mido import MidiFile
import os, copy

path = "/Users/Bernat/Dropbox/UoE/Dissertation/midiFiles/"
testPath = "/Users/Bernat/Dropbox/UoE/Dissertation/testMidi/"

def splitChannels(fileName):
	mid = MidiFile(path + fileName)

	for i, track in enumerate(mid.tracks):
		if i==0:
			continue
		newMid = MidiFile()
		newMid.tracks.append(mid.tracks[0])
		newMid.tracks.append(mid.tracks[i])
		name = "testtrack_%d.mid" % (i)
		newMid.save(testPath + name)

def addSteps():
	seqNumSteps = [] #array of number of timesteps per song
	for fileName in os.listdir(path): #iterate per file
		if ".mid" in fileName:
			mid = MidiFile(path + fileName)
			for i, track in enumerate(mid.tracks):
				if i == 0: #first track contains meta-messages only
					numSteps = 0
					for message in track:
						numSteps += message.time
					seqNumSteps.append(numSteps)
					break
	return sum(seqNumSteps)

#splitChannels("000101b_.mid")
print addSteps()


