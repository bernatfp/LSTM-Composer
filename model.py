#Imports



#Load data


#Transform data to 3d tensor of dimensions (nb_samples, timesteps, input_dim)


#Build model
print('Build model...')
model = Sequential()
model.add(LSTM(input_dim, input_dim))
model.compile(loss='binary_crossentropy', optimizer='adam', class_mode="binary")

#Train
print("Train...")
model.fit(X_train, y_train, batch_size=batch_size, nb_epoch=5, validation_split=0.1, show_accuracy=True)
score = model.evaluate(X_test, y_test, batch_size=batch_size)
print('Test score:', score)

#Save model
model.save_weights("/Users/Bernat/Dropbox/UoE/Dissertation/testMidi/model%d.h5" % int(time.time()))

#Predict
print ("Composing new song...")
song = []
x = [0] * input_dim
for i in xrange(100000):
	x = model.predict(x, batch_size=1)
	song.append(x)

#Save data to midi file