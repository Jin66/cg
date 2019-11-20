import pickle
from os.path import isfile


def save_object(object_to_save, filename):
    with open(filename, 'wb') as output_file:
        pickle.dump(object_to_save, output_file)


def load_object(filename):
    if isfile(filename):
        with open(filename, 'rb') as input_file:
            return pickle.load(input_file)
    else:
        return None
