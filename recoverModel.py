#Run python -i recoverModel.py <modeldir> to set the environment to play with the

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

if len(sys.argv) < 2:
	print("Please specify directory for the model")

print("Loading params...")
path = sys.argv[1] if sys.argv[1][-1] == '/' else sys.argv[1] + '/'
params = dataUtils.loadData(path + "params.nn")

print("Loading data...")
roll = dataUtils.createRepresentation("/Users/Bernat/Dropbox/UoE/Dissertation/midiFiles/", limitSongs=params["limitSongs"], reductionRatio=params["reductionRatio"]) #array of "piano roll" like representations

print("Regenerating inputs")
X, Y = dataUtils.createModelInputs(roll, padding=params["padding"], seqLength=params["seqLength"], inc=params["inc"])
X, Y, notesMap = dataUtils.compressInputs(X, Y)
Y = np.delete(Y, list([53,55]), 1)
notesMap.remove(87)
notesMap.remove(89)
input_dim = len(notesMap)

if notesMap != params["notesMap"]:
	print("Notes maps don't match!")
	print(notesMap)
	print(params["notesMap"])

print("Building model...")
input_dim = params["inputDim"]
model = Sequential()
model.add(LSTM(input_dim, input_dim*2, return_sequences=True))
model.add(Dense(input_dim*2, input_dim*2))
model.add(LSTM(input_dim*2, input_dim))

print("Compiling model...")
model.compile(loss='binary_crossentropy', optimizer='adam', class_mode="binary")

print("Loading weights...")
model.load_weights(path + "model.h5")



print("Done")

#mmd, mkmat = modelUtils.evalModel(model, roll, X, params, 20)

