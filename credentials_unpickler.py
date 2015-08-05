import pickle

def unpickle(account):
    filename = "%s.pickle" % account
    
    with open(filename, 'rb') as f:
        credentials = pickle.load(f)
    
    return credentials