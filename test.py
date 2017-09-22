import utils, torch, time, os, pickle, cv2
import numpy as np
import torch.nn as nn
import torch.optim as optim
from torch.autograd import Variable
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

transform = transforms.Compose([transforms.ToTensor(),transforms.Normalize((0.5,0.5,0.5),(0.5,0.5,0.5))])
obj = utils.load_wood('data/wood/ok', transform=transform)
data_loader = DataLoader(obj, batch_size=64,shuffle=True)
#print(data_loader.dataset.__len__())
#obj = utils.load_wood()
#print(obj.__dict__)
#print(dataset.image_paths)
for iter, (x_, _) in enumerate(data_loader):
    if iter == data_loader.dataset.__len__() // 64:
        print('dadada')
        break
    print(iter)
    #print(x)
    #print(y)
   
