import os
from os import path
import pickle
import pprint

folders = dict()
smap = open('smap','wb')

def start(root):
    dirsearch(root)
    pickle.dump(folders,smap)
    smap.close()

def dirsearch(root):
    folders[root]={'items': dict()}
    for i in os.listdir(root):
        if os.path.isdir(os.path.join(root,i)):
            dirsearch(os.path.join(root,i))
        folders[root]['items'][i] = os.path.join(root,i)
