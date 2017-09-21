import utils, torch, time, os, pickle, cv2
import numpy as np
import torch.nn as nn
import torch.optim as optim
from torch.autograd import Variable
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

dataset = utils.load_wood('data/wood')

print(len(dataset))
#print(dataset.labels[0])
for iter, x in enumerate(dataset):
    if iter == dataset.imgs.__len__():
        print('dadada')
        break
    print(iter)
    #print(x)
   
