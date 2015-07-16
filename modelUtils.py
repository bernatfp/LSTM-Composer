from keras.callbacks import Callback
import numpy as np
import copy

import dataUtils

class LossHistory(Callback):
	def on_train_begin(self, logs={}):
		self.losses = []

	def on_batch_end(self, batch, logs={}):
		self.losses.append(logs.get('loss'))


def generateSong(model, kickstart, method="sample", chunkLength=20, songLength=3000):
	if method == "sample":
		createOutput = dataUtils.sampleOutput
	elif method == "threshold":
		createOutput = dataUtils.thresholdOutput
	else:
		print "Error, method %s does not exist!" % (method)
		return ([],[])

	probs = []
	song = np.copy(kickstart)

	for i in xrange(songLength):
		lastnotes = np.array([song[-chunkLength:]])
		x = model.predict(lastnotes, batch_size=1)
		probs.extend(np.copy(x))
		x[0] = createOutput(x[0])
		song = np.concatenate((song, x))

	return (song, probs)