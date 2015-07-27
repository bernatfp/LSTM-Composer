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

