import os, gzip, torch
import cv2
import glob
import torch.nn as nn
import numpy as np
import scipy.misc
import imageio
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from PIL import Image
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms

def load_mnist(dataset):
    data_dir = os.path.join("./data", dataset)

    def extract_data(filename, num_data, head_size, data_size):
        with gzip.open(filename) as bytestream:
            bytestream.read(head_size)
            buf = bytestream.read(data_size * num_data)
            data = np.frombuffer(buf, dtype=np.uint8).astype(np.float)
        return data

    data = extract_data(data_dir + '/raw/train-images-idx3-ubyte.gz', 60000, 16, 28 * 28)
    trX = data.reshape((60000, 28, 28, 1))

    data = extract_data(data_dir + '/raw/train-labels-idx1-ubyte.gz', 60000, 8, 1)
    trY = data.reshape((60000))

    data = extract_data(data_dir + '/raw/t10k-images-idx3-ubyte.gz', 10000, 16, 28 * 28)
    teX = data.reshape((10000, 28, 28, 1))

    data = extract_data(data_dir + '/raw/t10k-labels-idx1-ubyte.gz', 10000, 8, 1)
    teY = data.reshape((10000))

    trY = np.asarray(trY).astype(np.int)
    teY = np.asarray(teY)

    X = np.concatenate((trX, teX), axis=0)
    y = np.concatenate((trY, teY), axis=0).astype(np.int)

    seed = 547
    np.random.seed(seed)
    np.random.shuffle(X)
    np.random.seed(seed)
    np.random.shuffle(y)

    y_vec = np.zeros((len(y), 10), dtype=np.float)
    for i, label in enumerate(y):
        y_vec[i, y[i]] = 1

    X = X.transpose(0, 3, 1, 2) / 255.
    # y_vec = y_vec.transpose(0, 3, 1, 2)

    X = torch.from_numpy(X).type(torch.FloatTensor)
    y_vec = torch.from_numpy(y_vec).type(torch.FloatTensor)
    return X, y_vec

def print_network(net):
    num_params = 0
    for param in net.parameters():
        num_params += param.numel()
    print(net)
    print('Total number of parameters: %d' % num_params)

def save_images(images, size, image_path):
    return imsave(images, size, image_path)

def imsave(images, size, path):
    image = np.squeeze(merge(images, size))
    return scipy.misc.imsave(path, image)

def merge(images, size):
    h, w = images.shape[1], images.shape[2]
    if (images.shape[3] in (3,4)):
        c = images.shape[3]
        img = np.zeros((h * size[0], w * size[1], c))
        for idx, image in enumerate(images):
            i = idx % size[1]
            j = idx // size[1]
            img[j * h:j * h + h, i * w:i * w + w, :] = image
        return img
    elif images.shape[3]==1:
        img = np.zeros((h * size[0], w * size[1]))
        for idx, image in enumerate(images):
            i = idx % size[1]
            j = idx // size[1]
            img[j * h:j * h + h, i * w:i * w + w] = image[:,:,0]
        return img
    else:
        raise ValueError('in merge(images,size) images parameter ''must have dimensions: HxW or HxWx3 or HxWx4')

def generate_animation(path, num):
    images = []
    for e in range(num):
        img_name = path + '_epoch%03d' % (e+1) + '.png'
        images.append(imageio.imread(img_name))
    imageio.mimsave(path + '_generate_animation.gif', images, fps=5)

def loss_plot(hist, path = 'Train_hist.png', model_name = ''):
    x = range(len(hist['D_loss']))

    y1 = hist['D_loss']
    y2 = hist['G_loss']

    plt.plot(x, y1, label='D_loss')
    plt.plot(x, y2, label='G_loss')

    plt.xlabel('Iter')
    plt.ylabel('Loss')

    plt.legend(loc=4)
    plt.grid(True)
    plt.tight_layout()

    path = os.path.join(path, model_name + '_loss.png')

    plt.savefig(path)

def initialize_weights(net):
    for m in net.modules():
        if isinstance(m, nn.Conv2d):
            m.weight.data.normal_(0, 0.02)
            m.bias.data.zero_()
        elif isinstance(m, nn.ConvTranspose2d):
            m.weight.data.normal_(0, 0.02)
            m.bias.data.zero_()
        elif isinstance(m, nn.Linear):
            m.weight.data.normal_(0, 0.02)
            m.bias.data.zero_()

'''custom dataset compatible with rebuilt DataLoader'''
def load_celebA(data_dir, batch_size):
    transform = transforms.Compose([transforms.CenterCrop(160), transforms.Scale(64), transforms.ToTensor()])
    dataset = celeba_folder(data_dir, transform)
    data_loader = DataLoader(dataset=dataset, batch_size=batch_size, shuffle=True)

    return data_loader

class celeba_folder(Dataset):
    '''celebA dataset'''
    def __init__(self, data_dir, transform=None):
        self.image_paths = list(map(lambda x: os.path.join(data_dir, x), os.listdir(data_dir)))
        self.transform = transform

    def __getitem__(self, index):
        image_path = self.image_paths[index]
        image = Image.open(image_path).convert('RGB')
        label = 1
        if self.transform is not None:
            image = self.transform(image)
        return image, label

    def __len__(self):
        return len(self.image_paths)    

def load_wood(data_dir, batch_size):
    transform = transforms.Compose([transforms.Scale(64), transforms.ToTensor()]) # do not need to normalize
    dataset = wood_folder(data_dir, transform)
    data_loader = DataLoader(dataset=dataset, batch_size=batch_size, shuffle=True)

    return data_loader

class wood_folder(Dataset):    
    '''wood texture dataset'''

    def __init__(self, data_dir, transform=None):
        '''initialize image paths and preprocessing module'''
        # collect image paths using map
        self.image_paths = list(map(lambda x: os.path.join(data_dir, x), os.listdir(data_dir)))
        self.transform = transform

    def __getitem__(self, index):
        '''reads an image from a file and preprocesses it and returns'''
        image_path = self.image_paths[index]
        #print(image_path)
        size = 64
        #print(image_path)
        image = Image.open(image_path).convert('RGB')
        #image = image.resize((size,size), Image.ANTIALIAS)
        label = 1
        if self.transform is not None:
            image = self.transform(image)
        return image, label
 
    def __len__(self):
        '''return the total number of image files'''
        #print(len(self.image_paths))
        return len(self.image_paths)
