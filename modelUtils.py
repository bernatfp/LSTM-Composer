from keras.callbacks import Callback
import numpy as np
import copy, ConfigParser
import dataUtils


def loadIni(name):
	config = ConfigParser.ConfigParser()
	config.read(name)

	params = {}

	params["dataDir"] = config.get("data", "data-dir") or "./"
	params["limitSongs"] = int(config.get("data", "limit-songs")) or 1
	params["inc"] = int(config.get("data", "inc")) or 1
	params["seqLength"] = int(config.get("data", "seq-length")) or 50
	params["padding"] = bool(config.get("data", "padding")) or True
	params["reductionRatio"] = int(config.get("data", "reduction-ratio")) or 128

	params["epochs"] = int(config.get("model", "epochs")) or 100
	params["batchSize"] = int(config.get("model", "batch-size")) or 12
	params["resultsDir"] = config.get("model", "results-dir") or "./"

	if params["dataDir"][-1] != '/':
		params["dataDir"] += '/'

	if params["resultsDir"][-1] != '/':
		params["resultsDir"] += '/'
	
	return params


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
		print("Error, method %s does not exist!" % (method))
		return ([],[])

	probs = []
	song = np.copy(kickstart)

	for i in xrange(songLength):
		lastnotes = np.array([song[-chunkLength:]])
		x = model.predict(lastnotes, batch_size=1)
		probs.extend(np.copy(x))
		x[0] = createOutput(x[0])
		if x[0][-1] == 1:
			print("End of song at ts %d/%d" % (i, songLength))
			break

		song = np.concatenate((song, x))

	return (song, probs)

