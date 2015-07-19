This is the code repository for my Master's Thesis work, in Algorithmic Music Composition using Recurrent Neural Networks (RNN).

I'm currently testing different Long-Short Term Memory (LSTM) based models using the Keras library.

The main file, and the one that should be run, is `model.py`. That's the one that creates, trains and evaluates the model. The script will run with the configuration specified by default on `config.ini`. If you wish to load a different configuration file, please pass the file path as an argument to the script call: `python model.py <myconfigfile.ini>` 

My approach to learning from musical pieces is to load .mid files into the model and translate the musical pieces to a "piano roll" like representation. All the necessary functions are contained within the `dataUtils.py` file. This file includes helper functions to convert from the MIDI format to a binary time discretized (what I call "piano roll" format) and the other way around, it also provides functions to reduce the size of the data considerably without losing much detail, mainly for performance purposes.

As a last note, this repository is still in active development as I keep trying more approaches to my area of research, so it might not be completely stable at all times. If you have any issues with running the code, please let me know.
