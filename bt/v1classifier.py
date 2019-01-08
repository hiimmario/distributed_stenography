# Generate dummy data
# x_train = np.random.random((100, 100, 100, 3))
# y_train = keras.utils.to_categorical(np.random.randint(10, size=(100, 1)), num_classes=10)
# x_test = np.random.random((20, 100, 100, 3))
# y_test = keras.utils.to_categorical(np.random.randint(10, size=(20, 1)), num_classes=10)

import shutil
from PIL import Image
import os
from pathlib import Path
from random import shuffle
from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten
from keras.layers import Conv2D, MaxPooling2D
import numpy as np
from keras.optimizers import SGD
from keras import metrics
import matplotlib.pyplot as plt

Image.MAX_IMAGE_PIXELS = 1000000000

def get_image_size_statistics(dir):
    heights = []
    widths = []
    img_count = 0

    files = [p for p in dir.iterdir() if p.is_file()]

    for idx, p in enumerate(files):
        with p.open() as file:
            data = np.array(Image.open(file.name))
            heights.append(data.shape[0])
            widths.append(data.shape[1])
            img_count += 1

    avg_height = sum(heights) / len(heights)
    avg_width = sum(widths) / len(widths)
    print("Average Height: " + str(avg_height))
    print("Max Height: " + str(max(heights)))
    print("Min Height: " + str(min(heights)))
    print("Average Width: " + str(avg_width))
    print("Max Width: " + str(max(widths)))
    print("Min Width: " + str(min(widths)))
    print("Count: " + str(img_count))


def load_training_data(path_original, path_manipulated):

    manipulated_files = [p for p in path_manipulated.iterdir() if p.is_file()]
    original_files = [p for p in path_original.iterdir() if p.is_file()]

    train_data = []
    test_data = []

    for idx, img in enumerate(manipulated_files):
        img = Image.open(img)
        img = img.convert('L')
        img = img.resize((IMG_SIZE, IMG_SIZE), Image.ANTIALIAS)
        if idx % 5 == 0:
            test_data.append([np.array(img), np.array([1, 0])])
        else:
            train_data.append([np.array(img), np.array([1, 0])])

        # plt.imshow(img)
        # plt.show()

    for idx, img in enumerate(original_files):
        img = Image.open(img)
        img = img.convert('L')
        img = img.resize((IMG_SIZE, IMG_SIZE), Image.ANTIALIAS)
        if idx % 5 == 0:
            test_data.append([np.array(img), np.array([0, 1])])
        else:
            train_data.append([np.array(img), np.array([0, 1])])

        # plt.imshow(img)
        # plt.show()

    shuffle(train_data)
    shuffle(test_data)

    print("len training data:\t" + str(len(train_data)))
    print("len test data:\t" + str(len(test_data)))

    return train_data, test_data


# move images from rt to proper bt folder for cwd usage
def move_images():
    target_directory_original = "/home/mario/Desktop/code/distributed_stenography/bt/data/originals"
    target_directory_manipulated = "/home/mario/Desktop/code/distributed_stenography/bt/data/manipulated"

    source_directory_original = "/home/mario/Desktop/code/distributed_stenography/rt/originals"
    source_directory_manipulated = "/home/mario/Desktop/code/distributed_stenography/rt/manipulated"

    if os.path.exists(target_directory_manipulated):
        shutil.rmtree(target_directory_manipulated)

    if os.path.exists(target_directory_original):
        shutil.rmtree(target_directory_original)

    shutil.copytree(source_directory_original, target_directory_original)
    shutil.copytree(source_directory_manipulated, target_directory_manipulated)


# move images from rt to bt folder forced overwrite!
# move_images()

IMG_SIZE = 300
# get image size statistics manipulated
cwd = os.getcwd()
path_source_originals = Path(cwd + "/data/originals")
path_source_manipulated = Path(cwd + "/data/manipulated")

# originals == manipulated
#print("size statistics images:")
#get_image_size_statistics(path_source_originals)

# prepare container for keras
training_data, test_data = load_training_data(path_source_originals, path_source_manipulated)

print(training_data)

trainImages = np.array([i[0] for i in training_data]).reshape(-1, 300, 300, 1)
trainLabels = np.array([i[1] for i in training_data])

validationImages = trainImages[:]
input_shape = (IMG_SIZE, IMG_SIZE, 1)

print(len(trainImages))
print(len(trainLabels))

x_train = trainImages[-100:]
y_train = trainLabels[-100:]
x_test = trainImages[0:len(trainImages)-100:]
y_test = trainLabels[0:len(trainImages)-100:]

print(len(x_train))
print(len(y_train))
print(len(x_test))
print(len(y_test))

# Convolution network
model = Sequential()
model.add(Conv2D(32, (3, 3), activation='relu', input_shape=(300, 300, 1)))
model.add(Conv2D(32, (3, 3), activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))

model.add(Conv2D(64, (3, 3), activation='relu'))
model.add(Conv2D(64, (3, 3), activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))

model.add(Flatten())
model.add(Dense(256, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(2, activation='softmax'))

sgd = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=["mse", "mae", "mape", "cosine", "acc"])

model.fit(x_train, y_train, batch_size=32, epochs=2, verbose=1)
score = model.evaluate(x_test, y_test, batch_size=32)

print(score)

plt.plot(model.history['acc'])
plt.plot(score.history['acc'])
plt.show()