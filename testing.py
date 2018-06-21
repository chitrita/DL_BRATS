import dictionary
import SimpleITK as sitk
import matplotlib.pyplot as plt
import numpy as np
import numpy.ma as ma
import random as rand
import os

if not os.path.exists('./preprocess/'):
    os.makedirs('./preprocess/')

#dictionary of patients (keys: patient ids, values: image paths)
#training dictionary
dct = dictionary.get() #length = 274

#test dictionary
dctTest = dictionary.getTrainig() #length = 110

def getMaskedArray(i, mod):
    '''returns cropped array, where values 0 are masked'''
    arr = sitk.GetArrayFromImage(sitk.ReadImage(dct[i][mod]))[77 - 64:77 + 64, 128 - 80:128 + 80, 120 - 72:120 + 72]
    return ma.masked_values(arr,0)

#calculating the average value and standard deviation
def getAvg(modality = 0):
    try:
        avg = np.load('./preprocess/avg{}.npy'.format(modality))
        return avg
    except IOError:
        print('AVG for modality {} not found, generating average'.format(modality))
    n = np.uint64(0)
    sum = np.uint(0)
    for d in dct:
        buffer = getMaskedArray(d, modality)
        sum += buffer.sum()
        n += ma.count(buffer)  # 326.62273804171326
        #n += buffer.size - ma.count_masked(buffer)  #326.62273804171326
    avg = np.float32(sum/n)
    np.save('./preprocess/avg{}.npy'.format(modality), avg)
    return(avg)

def getStd(modality = 0):
    try:
        avg = np.load('./preprocess/std{}.npy'.format(modality))
        return avg
    except IOError:
        print('STD for modality {} not found, generating std'.format(modality))
    n = np.uint64(0)
    sum = np.uint(0)
    avg = getAvg(modality=modality)
    for d in dct:
        buffer = getMaskedArray(d, modality)
        sum += np.square(buffer - avg).sum()
        n += ma.count(buffer)  # 326.62273804171326
        # n += buffer.size - ma.count_masked(buffer)  #326.62273804171326
    std = np.float32(np.sqrt(np.divide(sum, n)))
    np.save('./preprocess/std{}.npy'.format(modality), std)
    return(std)

"""print('flair')
print(getAvg(0))
print(getStd(0))
print('t1')
print(getAvg(1))
print(getStd(1))
print('t1c')
print(getAvg(2))
print(getStd(2))
print('t2')
print(getAvg(3))
print(getStd(3))"""


def standardize(arr, mod):
    return (arr-getAvg(mod))/(getStd(mod) + 0.000000001)


def getBatchTraining():     #  Zanekrat je ozadje 0  -da ne vpliva na gradient
                    #  Lahko spremeniš z tem, da daš filled v standardize
    key = rand.choice(list(dct))
    arr = []
    answers = outputToChannels(key)
    for i in range(4):
        arr.append(standardize(getMaskedArray(key, mod =i),
                               i))

    data = np.ma.masked_array(arr).filled(0)

    return np.expand_dims(data,0), np.expand_dims(answers,0)


#print(getN(2))
#print(getN(1))

def outputToChannels(id):
    """ ta koda je sexy """
    arr = np.array(sitk.GetArrayFromImage(sitk.ReadImage(dct[id][4])))[77 - 64:77 + 64, 128 - 80:128 + 80, 120 - 72:120 + 72]
    zeros = np.expand_dims(np.zeros(arr.size),0)  # or shape...
    buffer = np.zeros(arr.size)
    buffer = np.append([buffer, buffer, buffer, buffer], zeros, 0)
    flat = arr.flatten()
    buffer[flat, np.arange(arr.size)] = 1
    [x,y,z] = arr.shape
    return np.reshape(buffer, newshape=(5,x,y,z)) # [1:]

def outputToChannelsTest(id):
    arr = np.array(sitk.GetArrayFromImage(sitk.ReadImage(dct[id][4])))[77 - 64:77 + 64, 128 - 80:128 + 80, 120 - 72:120 + 72]

    type0 = np.zeros(arr.shape)
    type0[arr==0] = 1

    type1 = np.zeros(arr.shape)
    type1[arr == 1] = 1

    type2 = np.zeros(arr.shape)
    type2[arr==2]=1

    type3 = np.zeros(arr.shape)
    type3[arr == 3] = 1

    type4 = np.zeros(arr.shape)
    type4[arr == 4]=1

    return np.stack((type0,type1,type2,type3,type4))

input, output = getBatchTraining()


"""def getBatch(size = 15, min= 0, max = 146):              BATCH SIZE je 1!!!
    arr = []
    for i in range(size):
        int = np.random.randint(min, max, None)
        for m in range(4):
            arr.append(standardize)
getMaskedArray(1, 0)"""

"""heh = outputToChannels(3)
print(outputToChannels(3))
plt.imshow(heh[4,65])
plt.show()
plt.imshow(heh[3,65])
plt.show()
plt.imshow(heh[2,65])
plt.show()
plt.imshow(heh[1,65])
plt.show()
plt.imshow(heh[0,65])
plt.show()
#def loss(a, b):"""

#print(np.array(sitk.GetArrayFromImage(sitk.ReadImage(dct[3][0]))[77-64:77+64,128-80:128+80,120-72:120+72]).shape)
#print(getN()) #(267839313.0, 87254322490.0, 44531328854.0)


"""arr = []
arr10m = []
arr10s = []
for idx, d in tqdm(enumerate(dct)):

    arr.append(ma.masked_values(sitk.GetArrayFromImage(sitk.ReadImage(dct[d][0])), 0))
    if idx%10 == 0:
        arr10m.append(np.mean(arr))
        arr10s.append(np.std(arr))
        arr = []
    #print(np.array(arr).shape)
#arr = np.array(arr10)
m = np.mean(arr10m)
s = np.mean(arr10s)
print(np.array([m,s]))

#np.save('C:/BRATS/meanstd1.npy', [m,s])
print(np.load('C:/BRATS/meanstd.npy'))

arr = []
for d in tqdm(dct):
    arr.append(ma.masked_values(sitk.GetArrayFromImage(sitk.ReadImage(dct[d][2])), 0))
    #print(np.array(arr).shape)
arr = np.array(arr)
m = np.mean(arr)
s = np.std(arr)
np.save('C:/BRATS/meanstd2.npy', [m,s])
print('saved2')
arr = []
for d in tqdm(dct):
    arr.append(ma.masked_values(sitk.GetArrayFromImage(sitk.ReadImage(dct[d][3])), 0))
    #print(np.array(arr).shape)
arr = np.array(arr)
m = np.mean(arr)
s = np.std(arr)
np.save('C:/BRATS/meanstd3.npy', [m,s])
print('saved3')
print(np.load('C:/BRATS/meanstd.npy'))
print(np.load('C:/BRATS/meanstd1.npy'))
print(np.load('C:/BRATS/meanstd2.npy'))
print(np.load('C:/BRATS/meanstd3.npy'))"""


"""arr = sitk.GetArrayFromImage(sitk.ReadImage(dct[10][2]))
(z,y,x) = arr.shape  # 155 240 240  --> 128 144 160  t(160  144  128)

arr_cropped = arr[77-64:77+64,128-80:128+80,120-72:120+72]
print(np.mean(arr_cropped))
arr_cropped = ma.masked_values(arr_cropped, 0)
print(np.mean(arr_cropped))
arr_cropped = (arr_cropped - np.mean(arr_cropped))/np.std(arr_cropped)

print(Patient(5).input_arrays.shape)
plt.imshow(Patient(5).input_arrays[3,64])
plt.show()


#he = Patient(25)
#print(he.dirs)"""


#displays a 3D picture
def display_numpy(picture):
    fig = plt.figure()
    iter = int(len(picture) /30)
    for num,slice in enumerate(picture):
        if num>=30:
            break
        y = fig.add_subplot(5,6,num+1)

        y.imshow(picture[num*iter], cmap='gray')
    plt.show()
    return


def save_numpy(picture, batch, dir='C:/activations/', filename = "/graph.png"):
    if not os.path.exists(dir):
        os.makedirs(dir + '{}'.format(batch))
    #dct = dictionary.get()
    savedir = dir + '{}/'.format(batch)
    fig = plt.figure()
    iter = int(len(picture) /30)
    for num,slice in enumerate(picture):
        if num>=30:
            break
        y = fig.add_subplot(5,6,num+1)

        y.imshow(picture[num*iter], cmap='gray')
    plt.savefig(dir + str(batch)+filename, dpi=500, format = "png")
    plt.close('all')
    #plt.show()
    return

"""display_numpy(outputToChannels(10)[0])
display_numpy(outputToChannels(10)[1])
display_numpy(outputToChannels(10)[2])
display_numpy(outputToChannels(10)[3])"""

