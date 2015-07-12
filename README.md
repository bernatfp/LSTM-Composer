This is the code repository for my Master's Thesis work, in Algorithmic Music Composition using Recurrent Neural Networks (RNN).

I'm currently testing different Long-Short Term Memory (LSTM) based models using the Keras library.

The main file, and the one that should be run, is `model.py`. That's the one that creates, trains and evaluates the model.

My approach to learning from musical pieces is to load .mid files into the model and translate the musical pieces to a "piano roll" like representation. All the necessary functions are contained within the `dataUtils.py` file. This file includes helper functions to convert from the MIDI format to a binary time discretized (what I call "piano roll" format) and the other way around, it also provides functions to reduce the size of the data considerably without losing much detail, mainly for performance purposes.

If you intend to use this code, please make sure you change the relevant variables in this code (namely `dataset_path` and `test_path`) that I have hardcoded to fulfill my needs (my apologies, I plan to switch to a better solution soon). 
