#Imports
import dataUtils, modelUtils
import numpy as np
import os, time, sys

from keras.models import Sequential
from keras.layers.core import Dense, Dropout
from keras.layers.recurrent import LSTM
from keras.callbacks import ModelCheckpoint

#We need to ensure we're using Python 2.7.x for it to work
if sys.version_info[0] is not 2 and sys.version_info[1] is not 7:
	print("Please run this program with Python 2.7")
	sys.exit(-1)

#Load configuration
print ("Loading configuration...")
params = modelUtils.loadIni(sys.argv[1] if len(sys.argv) == 2 else "config.ini")

print("Configuration: ")
for (key, value) in params.items():
	print(key + ":  " + str(value))

while 1:
	user_input = raw_input("Continue? [y]/n: ")
	if user_input == 'n':
		print("Exiting...")
		sys.exit(-1)
	elif user_input == 'y' or user_input == '':
		break
	else:
		print("Please press ENTER or 'y' if you want to continue, or 'n' if you wish to abort.")
		continue

#Load data
print("Loading data...")
roll = dataUtils.createRepresentation(params["dataDir"], limitSongs=params["limitSongs"], reductionRatio=params["reductionRatio"]) #array of "piano roll" like representations

#Transform 
print("Creating output sequences...")
X, Y = dataUtils.createModelInputs(roll, padding=params["padding"], seqLength=params["seqLength"], inc=params["inc"])
X, Y, notesMap = dataUtils.compressInputs(X, Y)
input_dim = len(notesMap)

#Training data shape:
# X -> (nb_samples, timesteps, input_dim) => "sequences of tones"
# Y -> (nb_samples, input_dim) => "next tone for every sequence"

#Build model
print("Building model...")
model = Sequential()
model.add(LSTM(input_dim, input_dim*2, return_sequences=True))
model.add(Dense(input_dim*2, input_dim*2))
model.add(LSTM(input_dim*2, input_dim))

print("Compiling model...")
model.compile(loss='binary_crossentropy', optimizer='adam', class_mode="binary")

#Train
print("Training...")
checkpointer = ModelCheckpoint(filepath="%stempmodel%d.h5" % (params["resultsDir"], int(time.time())), verbose=1, save_best_only=False)
history = modelUtils.LossHistory()
model.fit(X, Y, batch_size=params["batchSize"], nb_epoch=params["epochs"], callbacks=[checkpointer, history])

#Save model
print("Saving model and parameters...")
currentTime = int(time.time())
resultsDir = "%s%d/" % (params["resultsDir"], currentTime)
os.mkdir(resultsDir)
model.save_weights("%smodel.h5" % (resultsDir))
params["notesMap"] = notesMap
params["inputDim"] = input_dim
params["lossHistory"] = history.losses
dataUtils.saveData(params, "%sparams.nn" % (resultsDir))

#Predict
print("Composing new song...")
(song, energy) = modelUtils.generateSong(model, X[params["seqLength"]])

#Save data to representation and midi formats
print("Storing song representation")
dataUtils.saveData(song, "%ssongoutput" % (resultsDir))
print("Storing song in midi format")
mid = dataUtils.roll2midi(song, notesMap, params["reductionRatio"])
dataUtils.saveMidi(mid, resultsDir)

print "Finished execution at time %d" % (currentTime)
