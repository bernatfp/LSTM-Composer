#Imports
import dataUtils
import numpy as np
import os, time, sys

from keras.models import Sequential
from keras.layers.recurrent import LSTM

#We need to ensure we're using Python 2.7.x for it to work
if sys.version_info[0] is not 2 and sys.version_info[1] is not 7:
	print("Please run this program with Python 2.7")
	sys.exit(-1)

DICE = False
if "DICE" in os.environ and os.environ["DICE"] == '1':
	DICE = True

if DICE == False:
	print("Running on personal computer...")
	dataset_path = "/Users/Bernat/Dropbox/UoE/Dissertation/midiFiles/"
	test_path = "/Users/Bernat/Dropbox/UoE/Dissertation/testMidi/"
else:
	print("Running on DICE...")
	dataset_path = "/afs/inf.ed.ac.uk/user/s14/s1471922/Dissertation/midiFiles/"
	test_path = "/afs/inf.ed.ac.uk/user/s14/s1471922/Dissertation/testMidi/"


#Load data
print("Loading data...")
roll = dataUtils.createRepresentation(limitSongs=10) #array of "piano roll" like representations
input_dim = len(roll[0][0])

#Transform 
print("Creating output sequences...")
X, Y = dataUtils.createModelInputs(roll)


#Training data shape:
# X -> (nb_samples, timesteps, input_dim) => "sequences of tones"
# Y -> (nb_samples, input_dim) => "next tone for every sequence"

#Build model
print("Build model...")
model = Sequential()
model.add(LSTM(input_dim, input_dim))
model.compile(loss='binary_crossentropy', optimizer='adam', class_mode="binary")

#Train
print("Train...")
model.fit(X, Y, batch_size=12, nb_epoch=5, validation_split=0.1, show_accuracy=True)

#Save model
print("Saving model...")
model.save_weights("%smodel%d.h5" % (test_path, int(time.time())))

#Predict
print("Composing new song...")
song = np.zeros((1,1,input_dim))
for i in xrange(3000):
	x = model.predict(song, batch_size=1)
	song = np.array([np.concatenate((song[0],x))])

song[0][-1][50] = 1
song[0][-1][57] = 1
song[0][-1][82] = 1
for i in xrange(1000):
	x = model.predict(song, batch_size=1)
	song[0] = np.concatenate((song[0],x))

#Save data to midi file
dataUtils.saveRepresentation(song, "songoutput%d.nn" % int(time.time))
