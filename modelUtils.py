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
	params["modelDir"] = config.get("results", "model-dir") or "./"

	if params["dataDir"][-1] != '/':
		params["dataDir"] += '/'

	if params["resultsDir"][-1] != '/':
		params["resultsDir"] += '/'
	
	if params["modelDir"][-1] != '/':
		params["modelDir"] += '/'	

	return params


class LossHistory(Callback):
	def on_train_begin(self, logs={}):
		self.losses = []

	def on_batch_end(self, batch, logs={}):
		self.losses.append(logs.get('loss'))


def generateSong(model, kickstart, method="sample", normalize=False, chunkLength=20, songLength=3000):
	if method == "sample":
		createOutput = dataUtils.sampleOutput
	elif method == "threshold":
		createOutput = dataUtils.thresholdOutput
	else:
		print("Error, method %s does not exist!" % (method))
		return ([],[])

	probs = []
	song = np.copy(kickstart)
	startidx = kickstart.shape[0]

	for i in xrange(songLength):
		lastnotes = np.array([song[-chunkLength:]])
		x = model.predict(lastnotes, batch_size=1)
		x[0] = map(lambda el: el if el > 0 else 0, x[0])
		probs.extend(np.copy(x))
		x[0] = createOutput(x[0], normalize=normalize)
		#if x[0][-1] == 1:
		#	print("End of song at ts %d/%d" % (i, songLength))
		#	break

		song = np.concatenate((song, x))

	return (song[startidx:], probs)


def evalModelTesting(model, params):
	roll = dataUtils.createRepresentation(params["testDir"], limitSongs=50, reductionRatio=params["reductionRatio"])
	#remove songs that contain notes out of params["notesMap"]
	#only with Y, we can take the roll and remove the 1st dimension	
	Y = np.zeros((0,len(params["notesMap"])))
	count = 0
	for song in roll:
		songNotes = set()
		for i in range(song.shape[0]):
			for j in range(song.shape[1]):
				if song[i][j] == 1 and j not in songNotes:
					songNotes.add(j)
		if songNotes.issubset(set(params["notesMap"])):
			notesDel = set(range(129)).difference(params["notesMap"])
			song = np.delete(song, list(notesDel), 1)
			Y = np.concatenate((Y,song))
			count += 1

	print "%d songs" % count

	return evalModel(model, Y)

def evalModel(model, Y, N=20, k=4, m=1):	
	'''
	#Need to generate kickstarts from the roll for the model
	#print("Creating kickstarts")
	#X, Y = dataUtils.createModelInputs(roll, padding=params["padding"], seqLength=params["seqLength"], inc=params["inc"])
	#X, Y, notesMap = dataUtils.compressInputs(X, Y)
	#input_dim = len(notesMap)
	'''

	#generate N songs from model
	print("Sampling songs")
	originalSongs = []
	sampledSongs = []
	#chunkLength = 20
	#songLength = int(np.mean(map(lambda s: s.shape[0], roll)))
	for n in range(N):
		print("Song %d" % n)
		idx = np.random.uniform(1,Y.shape[0]-500)
		originalSongs.append(Y[idx:idx+500])
		idx = np.random.uniform(1,Y.shape[0]-500)
		sampledSongs.append(generateSong(model, Y[idx:idx+500], songLength=500, chunkLength=500)[0])
	
	#print("Expanding sampled songs...")
	#dataUtils.expandInputs(sampledSongs, params["notesMap"][:-1])
	



	#MMD
	#Call func
	mmd, mkmat = MMD(originalSongs, sampledSongs, N)

	return mmd, mkmat

def MMD(X, Y, N, k=4, m=1, normalized=False):
	#Precompute kernel of each instance
	normalized = np.zeros((N,2))
	for i in range(N):
		print i
		normalized[i][0] = mismatchKernel(X[i], X[i], k, m)
		normalized[i][1] = mismatchKernel(Y[i], Y[i], k, m)
	
	#MMD part: 
	#compare each one to the others using kernel
	MMD = 0.0
	mkmat = np.zeros((3,N,N)) - 1
	count = 1
	for i in range(N):
		for j in range(N):
			print("1st Mismatch Kernel: %d/%d" % (count, 3*N**2))
			count += 1
			if mkmat[0][j][i] >= 0:
				mkmat[0][i][j] = mkmat[0][j][i]
			#elif i==j:
			#	mkmat[0][i][j] = normalized[i][0]
			else:
				normalized_pair = [normalized[i][0], normalized[j][0]]
				mkmat[0][i][j] = mismatchKernel(X[i], X[j], k, m, normalized_pair)

			if i != j:
				MMD += 1.0/(N*(N-1)) * mkmat[0][i][j]

	for i in range(N):
		for j in range(N):
			print("2nd Mismatch Kernel: %d/%d" % (count, 3*N**2))
			count += 1
			if mkmat[1][j][i] >= 0:
				mkmat[1][i][j] = mkmat[1][j][i]
			#elif i==j:
			#	mkmat[1][i][j] = normalized[i][1]
			else:
				normalized_pair = [normalized[i][1], normalized[j][1]]
				mkmat[1][i][j] = mismatchKernel(Y[i], Y[j], k, m, normalized_pair)

			if i != j:
				MMD += 1.0/(N*(N-1)) * mkmat[1][i][j]

	for i in range(N):
		for j in range(N):
			print("3rd Mismatch Kernel: %d/%d" % (count, 3*N**2))
			count += 1
			if mkmat[2][j][i] >= 0:
				mkmat[2][i][j] = mkmat[2][j][i]
			else:
				normalized_pair = [normalized[i][0], normalized[j][1]]
				mkmat[2][i][j] = mismatchKernel(X[i], Y[j], k, m, normalized_pair)	
			MMD += 1.0/(N*N) * mkmat[2][i][j]

	return MMD, mkmat

def mismatchKernel(X, Y, k=4, m=1, normalized=None):
	matches = 0
	for i in xrange(X.shape[0]-(k-1)):
		for j in xrange(X.shape[0]-(k-1)):
			if sum(map(lambda x, y: 1 if np.array_equal(x, y) else 0, X[i:i+k], Y[j:j+k])) > m:
				#print "--------"
				#print X[i:i+k]
				#print Y[j:j+k]
				#print "--------"
				matches += 1

	if normalized is not None:
		return matches / (np.sqrt(normalized[0]) * np.sqrt(normalized[1]))

	print "Matches: %d" % (matches)

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
