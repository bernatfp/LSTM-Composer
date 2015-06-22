#Imports
import dataUtils
import numpy as np

from keras.models import Sequential
from keras.layers.recurrent import LSTM


#Load data
print("Loading data...")
X = dataUtils.createRepresentation(limitSongs=10)
input_dim = X.shape[2]

#Transform X to create Y
print("Creating output sequences...")
Y = np.zeros((X.shape[0], X.shape[2]))
'''
Y = np.zeros(X.shape[0])
for n in xrange(X.shape[0]):
	Y[n] = np.concatenate((X[n][1:], [X[n][0]]))
'''

#Training data shape -> (nb_samples, timesteps, input_dim)

#Build model
print("Build model...")
model = Sequential()
model.add(LSTM(input_dim, input_dim))
model.compile(loss='binary_crossentropy', optimizer='adam', class_mode="binary")

#Train
print("Train...")
model.fit(X, Y, batch_size=2, nb_epoch=5, validation_split=0.1, show_accuracy=True)

#Save model
model.save_weights("/Users/Bernat/Dropbox/UoE/Dissertation/testMidi/model%d.h5" % int(time.time()))

#Predict
print ("Composing new song...")
song = []
x = [0] * input_dim
for i in xrange(100000):
	x = model.predict(x, batch_size=1)
	song.append(x)
x = [0] * input_dim
x[50] = 1
x[57] = 1
x[82] = 1
for i in xrange(100000):
	x = model.predict(x, batch_size=1)
	song.append(x)

#Save data to midi file
dataUtils.saveRepresentation(song, "songoutput%d.nn" % int(time.time))