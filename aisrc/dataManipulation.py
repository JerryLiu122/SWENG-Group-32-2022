#Stage 1, preparing the data
import numpy as np 
import pandas as pd 
from sklearn.utils import resample
from sklearn.utils.class_weight import compute_class_weight
from sklearn.utils import class_weight
from keras.utils.np_utils import to_categorical 
import os
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error

#
#Function that loads in training and testing data
#
def readECGData ():
    
    current_directory = os.getcwd()   


    train = pd.read_csv(current_directory + '/data/mitbih_train.csv', header=None)
    test = pd.read_csv(current_directory + '/data/mitbih_test.csv', header=None)

    return train, test

def readECGDataLSTM ():
    
    current_directory = os.getcwd()   

    np.random.seed(7)
    dataframe = pd.read_csv(current_directory + '/data/mitbih_train.csv', usecols=[1], engine='python')
    dataset = dataframe.values
    dataset = dataset.astype('float32')
    scaler = MinMaxScaler(feature_range=(0, 1))
    dataset = scaler.fit_transform(dataset)

    train_size = int(len(dataset) * 0.67)
    test_size = len(dataset) - train_size
    train, test = dataset[0:train_size,:], dataset[train_size:len(dataset),:]
    return train, test


    
    return train, test

def create_dataset(dataset, look_back=1):
	dataX, dataY = [], []
	for i in range(len(dataset)-look_back-1):
		a = dataset[i:(i+look_back), 0]
		dataX.append(a)
		dataY.append(dataset[i + look_back, 0])
	return np.array(dataX), np.array(dataY)

def resampleData (data):
    
    data0 = (data[data[187]==0]).sample(n=20000,random_state=420)
    data1 = data[data[187]==1]
    data2 = data[data[187]==2]
    data3 = data[data[187]==3]
    data4 = data[data[187]==4]

    data1up = resample(data1,replace=True,n_samples=20000,random_state=10)
    data2up = resample(data2,replace=True,n_samples=20000,random_state=11)
    data3up = resample(data3,replace=True,n_samples=20000,random_state=12)
    data4up = resample(data4,replace=True,n_samples=20000,random_state=13)

    result = pd.concat([data0,data1up,data2up,data3up,data4up])
    
    return result

#function that calculates the class weighting for the weighted model, takes in imbalanced training data
def calculateWeights(trainingData):

    totalSize = trainingData.shape[0]
    freq = frequencyClasses(trainingData)

    weight0 = totalSize/(5*freq[0])
    weight1 = totalSize/(5*freq[1])
    weight2 = totalSize/(5*freq[2])
    weight3 = totalSize/(5*freq[3])
    weight4 = totalSize/(5*freq[4])

    classWeights = {"0":weight0,"1":weight1,"2":weight2,"3":weight3,"4":weight4}

    print(classWeights)

    return classWeights




def add_gaussian_noise(signal):
    noise=np.random.normal(0,0.5,186)
    return (signal+noise)

#function that returns frequencies of all classes from a dataset
def frequencyClasses (data):
    data[187]=data[187].astype(int)
    classcounts=data[187].value_counts()
    
    return classcounts


#function that returns formatted training and testing outputs
def formatOutputs (train, test):
    train_outputs = to_categorical(train[187])
    test_outputs = to_categorical(test[187])

    return train_outputs, test_outputs
  


#function that returns formatted training and testing inputs
def formatInputs (train, test):
    train_inputs = train.iloc[:,:186].values
    test_inputs = test.iloc[:,:186].values
    #X_train=result.iloc[:,:186].values
    #X_test=result.iloc[:,:186].values

    for i in range(len(train_inputs)):
        train_inputs[i,:186]= add_gaussian_noise(train_inputs[i,:186])
    train_inputs = train_inputs.reshape(len(train_inputs), train_inputs.shape[1],1)
    test_inputs = test_inputs.reshape(len(test_inputs), test_inputs.shape[1],1)
    #for i in range(len(X_train)):
    #    X_train[i,:186]= add_gaussian_noise(X_train[i,:186])
    #X_train = X_train.reshape(len(X_train), X_train.shape[1],1)
    #X_test = X_test.reshape(len(X_test), X_test.shape[1],1)

    return train_inputs, test_inputs

def reshapeInputs(train, test):
    look_back = 1
    trainX, trainY = create_dataset(train, look_back)
    testX, testY = create_dataset(test, look_back)
    trainX = np.reshape(trainX, (trainX.shape[0], 1, trainX.shape[1]))
    testX = np.reshape(testX, (testX.shape[0], 1, testX.shape[1]))
    return trainX, testX, trainY, testY