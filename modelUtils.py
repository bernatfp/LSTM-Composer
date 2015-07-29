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
	
	params["resultsDir"] = config.get("results", "results-dir") or "./"

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

#To Do: Rethink structure of the function. There's some very inefficient redundancies here
def evalModel(model, roll, X, params, N, k=4, m=1):	
	#limit number of songs
	N = min(N, len(roll))

	'''
	#Need to generate kickstarts from the roll for the model
	#print("Creating kickstarts")
	#X, Y = dataUtils.createModelInputs(roll, padding=params["padding"], seqLength=params["seqLength"], inc=params["inc"])
	#X, Y, notesMap = dataUtils.compressInputs(X, Y)
	#input_dim = len(notesMap)
	'''

	#generate N songs from model
	print("Sampling songs")
	sampledSongs = []
	chunkLength = 20
	songLength = int(np.mean(map(lambda s: s.shape[0], roll)))
	for n in range(N):
		print("Song %d" % n)
		sampledSongs.append(generateSong(model, X[n][-chunkLength:], "sample", chunkLength, songLength)[0])
	
	print("Expanding sampled songs...")
	dataUtils.expandInputs(sampledSongs, params["notesMap"][:-1])

	#MMD part: 
	#compare each one to the others using kernel
	MMD = 0
	mkmat = np.zeros((3,N,N))
	count = 1
	for i in range(N):
		for j in range(N):
			print("Mismatch Kernel: %d/%d" % (count, 3*N**2))
			count += 1
			mkmat[0][i][j] = mismatchKernel(roll[i], roll[j])
			if i != j:
				MMD += 1/(N*(N-1)) * mkmat[0][i][j]

	for i in range(N):
		for j in range(N):
			print("Mismatch Kernel: %d/%d" % (count, 3*N**2))
			count += 1
			mkmat[1][i][j] = mismatchKernel(sampledSongs[i], sampledSongs[j])
			if i != j:
				MMD += 1/(N*(N-1)) * mkmat[1][i][j]

	for i in range(N):
		for j in range(N):
			print("Mismatch Kernel: %d/%d" % (count, 3*N**2))
			count += 1
			mkmat[2][i][j] = mismatchKernel(sampledSongs[i], roll[j])	
			MMD += 1/(N*N) * mkmat[2][i][j]

	return MMD, mkmat

def MMD(X, Y, N, k=4, m=1, normalized=False):
	#MMD part: 
	#compare each one to the others using kernel
	MMD = 0.0
	mkmat = np.zeros((3,N,N)) - 1
	count = 1
	for i in range(N):
		for j in range(N):
			print("Mismatch Kernel: %d/%d" % (count, 3*N**2))
			count += 1
			if mkmat[0][j][i] >= 0:
				mkmat[0][i][j] = mkmat[0][j][i]
			elif i==j:
				mkmat[0][i][j] = len(X[i])-k+m
			else:
				mkmat[0][i][j] = mismatchKernel(X[i], X[j], k, m, normalized)

			if i != j:
				MMD += 1.0/(N*(N-1)) * mkmat[0][i][j]

	for i in range(N):
		for j in range(N):
			print("Mismatch Kernel: %d/%d" % (count, 3*N**2))
			count += 1
			if mkmat[1][j][i] >= 0:
				mkmat[1][i][j] = mkmat[1][j][i]
			elif i==j:
				mkmat[1][i][j] = len(X[i])-k+m
			else:
				mkmat[1][i][j] = mismatchKernel(Y[i], Y[j], k, m, normalized)

			if i != j:
				MMD += 1.0/(N*(N-1)) * mkmat[1][i][j]

	for i in range(N):
		for j in range(N):
			print("Mismatch Kernel: %d/%d" % (count, 3*N**2))
			count += 1
			if mkmat[2][j][i] >= 0:
				mkmat[2][i][j] = mkmat[2][j][i]
			else:
				mkmat[2][i][j] = mismatchKernel(Y[i], X[j], k, m, normalized)	
			MMD += 1.0/(N*N) * mkmat[2][i][j]

	return MMD, mkmat

def mismatchKernel(X, Y, k=4, m=1, normalized=False):
	matches = 0
	for i in xrange(X.shape[0]-(k-1)):
		for j in xrange(X.shape[0]-(k-1)):
			if sum(map(lambda x, y: 0 if np.array_equal(x, y) else 1, X[i:i+k], Y[j:j+k])) <= m:
				print "--------"
				print X[i:i+k]
				print Y[j:j+k]
				print "--------"
				matches += 1

	if normalized == True:
		return matches / (np.sqrt(mismatchKernel(X, X, k, m)) * np.sqrt(mismatchKernel(Y, Y, k, m)))

	return matches

def testMMD():
	N = 4
	testseq = np.zeros((10,5))
	for i in range(testseq.shape[0]):
		for j in range(testseq.shape[1]):
			testseq[i,j] = np.random.randint(2)

	X = np.zeros((N,testseq.shape[0],testseq.shape[1]))
	for i in range(X.shape[0]):
		X[i] = testseq

	#Y = X[:,::-1,:]
	Y = np.copy(X)
	Y[0,:,:] = np.zeros((10,5))

	return MMD(X, Y, N)
