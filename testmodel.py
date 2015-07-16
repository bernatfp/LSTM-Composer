from keras.models import Sequential
from keras.layers.core import Dense, Dropout
from keras.layers.recurrent import LSTM
import numpy as np
import copy

#instance1 = [[1,0,1,0,0],[0,1,0,1,0],[0,0,1,0,1],[1,0,0,1,0],[0,1,0,0,1],[1,0,1,0,0],[0,1,0,1,0],[0,0,1,0,1],[1,0,0,1,0],[0,1,0,0,1]]
#instance2 = [[1,1,0,0,0],[0,1,1,0,0],[0,0,1,1,0],[0,0,0,1,1],[1,0,0,0,1],[1,1,0,0,0],[0,1,1,0,0],[0,0,1,1,0],[0,0,0,1,1],[1,0,0,0,1]]
instance3 = [[1,1,0,0,0],[1,1,0,0,0],[0,0,1,1,0],[0,0,0,0,1],[1,0,0,0,1],[0,0,0,1,1],[0,0,1,1,0],[0,0,1,1,0],[1,1,0,0,0],[1,0,0,0,0]]
#data = np.array([instance1, instance2, instance3])
data = []
for i in range(len(instance3)):
	data.append(copy.deepcopy(instance3))
	instance3.append(instance3.pop(0))
data = np.array(data)

X = np.zeros((data.shape[0], data.shape[1]-1, data.shape[2]))
Y = np.zeros((data.shape[0], data.shape[2]))

for i in range(data.shape[0]):
	X[i] = data[i][:-1]
	Y[i] = data[i][-1]

'''#M1
model = Sequential()
model.add(LSTM(5, 5))
'''
#'''M2
model = Sequential()
model.add(LSTM(input_dim, input_dim*2, return_sequences=True))
model.add(Dense(input_dim*2, input_dim*2))
model.add(LSTM(input_dim*2, input_dim))
#'''



model.compile(loss='binary_crossentropy', optimizer='adam', class_mode="binary")

model.fit(X, Y, batch_size=1, nb_epoch=5000)


for i in xrange(1, data.shape[1]):
	d = np.array([data[0][:i]])
	model.predict(d)
	print data[0][i]


song = X[50]
energy = []
for i in xrange(300):
	lastnotes = np.array([song[-20:]])
	x = model.predict(lastnotes, batch_size=1)
	energy.extend(copy.copy(x))
	x[0] = dataUtils.sampleOutput(x[0])
	song = np.concatenate((song, x))

plt.matshow(np.transpose(song)); plt.show()
plt.matshow(np.transpose(energy)); plt.show()

'''
test1 = np.array([[X[2][0]]])
model.predict(test1)
print X[2][1]
test2 = np.array([X[2][0:2]])
model.predict(test2)
print X[2][2]
test3 = np.array([X[2][0:4]])
model.predict(test3)
print X[2][4]
test4 = np.array([X[2][0:6]])
model.predict(test4)
print X[2][6]
test5 = np.array([X[2][0:7]])
model.predict(test5)
print X[2][7]
test6 = np.array([X[2][0:8]])
model.predict(test6)
print X[2][8]
test7 = np.array([X[2][0:9]])
model.predict(test7)
print Y[2]
'''


mid = dataUtils.roll2midi(np.array([song[50:]]), notesMap)
