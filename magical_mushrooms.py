# -*- coding: utf-8 -*-
"""Magical Mushrooms.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1bo1t-lqBPUgG7aCGsc675luQJnBIDxRz
"""

#Install Wandb

!pip install -q wandb -U

# Commented out IPython magic to ensure Python compatibility.
import os
import requests
import zipfile
import tarfile
import shutil
import math
import json
import time
import sys
import cv2
import string
import re
import subprocess
import hashlib
import numpy as np
import pandas as pd
from glob import glob
import collections
import unicodedata
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.cm as cm
# %matplotlib inline

# Tensorflow
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import Model, Sequential
from tensorflow.keras.utils import to_categorical
from tensorflow.python.keras import backend as K
from tensorflow.python.keras.utils.layer_utils import count_params

from tensorflow.keras import layers, models
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.optimizers import Adam
# sklearn
from sklearn.model_selection import train_test_split

# Tensorflow Hub
import tensorflow_hub as hub

# Colab auth
from google.colab import auth
from google.cloud import storage

# W&B
import wandb
from wandb.integration.keras import WandbCallback

# Enable/Disable Eager Execution
# Reference: https://www.tensorflow.org/guide/eager
# TensorFlow's eager execution is an imperative programming environment that evaluates operations immediately,
# without building graphs

#tf.compat.v1.disable_eager_execution()
#tf.compat.v1.enable_eager_execution()

print("tensorflow version", tf.__version__)
print("keras version", tf.keras.__version__)
print("Eager Execution Enabled:", tf.executing_eagerly())

# Get the number of replicas
strategy = tf.distribute.MirroredStrategy()
print("Number of replicas:", strategy.num_replicas_in_sync)

devices = tf.config.experimental.get_visible_devices()
print("Devices:", devices)
print(tf.config.experimental.list_logical_devices('GPU'))

print("GPU Available: ", tf.config.list_physical_devices('GPU'))
print("All Physical Devices", tf.config.list_physical_devices())

# Better performance with the tf.data API
# Reference: https://www.tensorflow.org/guide/data_performance
AUTOTUNE = tf.data.experimental.AUTOTUNE

# def download_file(packet_url, base_path="", extract=False, headers=None):
#   if base_path != "":
#     if not os.path.exists(base_path):
#       os.mkdir(base_path)
#   packet_file = os.path.basename(packet_url)
#   with requests.get(packet_url, stream=True, headers=headers) as r:
#       r.raise_for_status()
#       with open(os.path.join(base_path,packet_file), 'wb') as f:
#           for chunk in r.iter_content(chunk_size=8192):
#               f.write(chunk)

#   if extract:
#     if packet_file.endswith(".zip"):
#       with zipfile.ZipFile(os.path.join(base_path,packet_file)) as zfile:
#         zfile.extractall(base_path)
#     else:
#       packet_name = packet_file.split('.')[0]
#       with tarfile.open(os.path.join(base_path,packet_file)) as tfile:
#         tfile.extractall(base_path)

# def compute_dataset_metrics(data_list):
#   data_list_with_metrics = []
#   for item in data_list:
#     # Read image
#     image = cv2.imread(item[1])
#     data_list_with_metrics.append((item[0],item[1],image.shape[0],image.shape[1],image.nbytes / (1024 * 1024.0)))

#   # Build a dataframe
#   data_list_with_metrics = np.asarray(data_list_with_metrics)
#   dataset_df = pd.DataFrame({
#     'label': data_list_with_metrics[:, 0],
#     'path': data_list_with_metrics[:, 1],
#     'height': data_list_with_metrics[:, 2],
#     'width': data_list_with_metrics[:, 3],
#     'size': data_list_with_metrics[:, 4],
#     })

#   dataset_df["height"] = dataset_df["height"].astype(int)
#   dataset_df["width"] = dataset_df["width"].astype(int)
#   dataset_df["size"] = dataset_df["size"].astype(float)

#   dataset_mem_size = dataset_df["size"].sum()
#   value_counts = dataset_df["label"].value_counts()
#   height_details = dataset_df["height"].describe()
#   width_details = dataset_df["width"].describe()

#   print("Dataset Metrics:")
#   print("----------------")
#   print("Label Counts:")
#   print(value_counts)
#   print("Image Width:")
#   print("Min:",width_details["min"]," Max:",width_details["max"])
#   print("Image Height:")
#   print("Min:",height_details["min"]," Max:",height_details["max"])
#   print("Size in memory:",round(dataset_df["size"].sum(),2),"MB")

# class JsonEncoder(json.JSONEncoder):
#   def default(self, obj):
#     if isinstance(obj, np.integer):
#         return int(obj)
#     elif isinstance(obj, np.floating):
#         return float(obj)
#     elif isinstance(obj, decimal.Decimal):
#         return float(obj)
#     elif isinstance(obj, np.ndarray):
#         return obj.tolist()
#     else:
#         return super(JsonEncoder, self).default(obj)

# experiment_name = None
# def create_experiment():
#   global experiment_name
#   experiment_name = "experiment_" + str(int(time.time()))

#   # Create experiment folder
#   if not os.path.exists(experiment_name):
#       os.mkdir(experiment_name)

# def upload_experiment(data_details):
#   # Check Bucket Access
#   bucket_name = "ac215-mushroom-app-models" # BUCKET NAME

#   # List buckets in a GCP project
#   storage_client = storage.Client(project="ac215-project") # PROJECT ID

#   # Get bucket for Experiments
#   bucket = storage_client.get_bucket(bucket_name)
#   print("Model Bucket:",bucket)

#   save_data_details(data_details)

#   # Copy the experiment folder to GCP Bucket
#   for file_path in glob(experiment_name+'/*'):
#     print(file_path)
#     blob = bucket.blob(os.path.join(user_account,file_path))
#     print('uploading file', file_path)
#     blob.upload_from_filename(file_path)

# def save_data_details(data_details):
#   with open(os.path.join(experiment_name,"data_details.json"), "w") as json_file:
#     json_file.write(json.dumps(data_details,cls=JsonEncoder))

# def save_model(model,model_name="model01"):

#   # Save the enitire model (structure + weights)
#   model.save(os.path.join(experiment_name,model_name+".hdf5"))

#   # Save only the weights
#   model.save_weights(os.path.join(experiment_name,model_name+".h5"))

#   # Save the structure only
#   model_json = model.to_json()
#   with open(os.path.join(experiment_name,model_name+".json"), "w") as json_file:
#       json_file.write(model_json)

# def get_model_size(model_name="model01"):
#   model_size = os.stat(os.path.join(experiment_name,model_name+".h5")).st_size
#   return model_size

# def append_training_history(model_train_history, prev_model_train_history):
#   for metric in ["loss","val_loss","accuracy","val_accuracy"]:
#     for metric_value in prev_model_train_history[metric]:
#       model_train_history[metric].append(metric_value)

#   return model_train_history

# def evaluate_save_model(model,test_data, model_train_history,execution_time, learning_rate, batch_size, epochs, optimizer,save=True):

#   # Get the number of epochs the training was run for
#   num_epochs = len(model_train_history["loss"])

#   # Plot training results
#   fig = plt.figure(figsize=(15,5))
#   axs = fig.add_subplot(1,2,1)
#   axs.set_title('Loss')
#   # Plot all metrics
#   for metric in ["loss","val_loss"]:
#       axs.plot(np.arange(0, num_epochs), model_train_history[metric], label=metric)
#   axs.legend()

#   axs = fig.add_subplot(1,2,2)
#   axs.set_title('Accuracy')
#   # Plot all metrics
#   for metric in ["accuracy","val_accuracy"]:
#       axs.plot(np.arange(0, num_epochs), model_train_history[metric], label=metric)
#   axs.legend()

#   plt.show()

#   # Evaluate on test data
#   evaluation_results = model.evaluate(test_data)
#   print(evaluation_results)

#   if save:
#     # Save model
#     save_model(model, model_name=model.name)
#     model_size = get_model_size(model_name=model.name)

#     # Save model history
#     with open(os.path.join(experiment_name,model.name+"_train_history.json"), "w") as json_file:
#         json_file.write(json.dumps(model_train_history,cls=JsonEncoder))

#     trainable_parameters = count_params(model.trainable_weights)
#     non_trainable_parameters = count_params(model.non_trainable_weights)

#     # Save model metrics
#     metrics ={
#         "trainable_parameters":trainable_parameters,
#         "execution_time":execution_time,
#         "loss":evaluation_results[0],
#         "accuracy":evaluation_results[1],
#         "model_size":model_size,
#         "learning_rate":learning_rate,
#         "batch_size":batch_size,
#         "epochs":epochs,
#         "optimizer":type(optimizer).__name__
#     }
#     with open(os.path.join(experiment_name,model.name+"_model_metrics.json"), "w") as json_file:
#         json_file.write(json.dumps(metrics,cls=JsonEncoder))

def download_file(packet_url, base_path="", extract=False, headers=None):
  if base_path != "":
    if not os.path.exists(base_path):
      os.mkdir(base_path)
  packet_file = os.path.basename(packet_url)
  with requests.get(packet_url, stream=True, headers=headers) as r:
      r.raise_for_status()
      with open(os.path.join(base_path,packet_file), 'wb') as f:
          for chunk in r.iter_content(chunk_size=8192):
              f.write(chunk)

  if extract:
    if packet_file.endswith(".zip"):
      with zipfile.ZipFile(os.path.join(base_path,packet_file)) as zfile:
        zfile.extractall(base_path)
    else:
      packet_name = packet_file.split('.')[0]
      with tarfile.open(os.path.join(base_path,packet_file)) as tfile:
        tfile.extractall(base_path)

start_time = time.time()
download_file("https://github.com/dlops-io/datasets/releases/download/v1.0/mushrooms_3_labels.zip", base_path="datasets", extract=True)
download_file("https://github.com/dlops-io/models/releases/download/v1.0/experiments.zip", base_path="experiments", extract=True)
execution_time = (time.time() - start_time)/60.0
print("Download execution time (mins)",execution_time)

base_path = os.path.join("datasets","mushrooms")
label_names = os.listdir(base_path)
print("Labels:", label_names)

# Number of unique labels
num_classes = len(label_names)
# Create label index for easy lookup
label2index = dict((name, index) for index, name in enumerate(label_names))
index2label = dict((index, name) for index, name in enumerate(label_names))

# Generate a list of labels and path to images
data_list = []
for label in label_names:
  # Images
  image_files = os.listdir(os.path.join(base_path,label))
  data_list.extend([(label,os.path.join(base_path,label,f)) for f in image_files])

print("Full size of the dataset:",len(data_list))
print("data_list:",data_list[:5])

# Generate a random sample of index
image_samples = np.random.randint(0,high=len(data_list)-1, size=12)

fig = plt.figure(figsize=(20,8))
for i,img_idx in enumerate(image_samples):
    axs = fig.add_subplot(3,4,i+1)
    axs.set_title(data_list[img_idx][0])
    # Read image
    image = cv2.imread(data_list[img_idx][1])
    # convert to rgb
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    plt.imshow(image)
    plt.axis('off')

plt.suptitle("Sample Images")
plt.show()

# # Compute dataset metrics
# compute_dataset_metrics(data_list)

# # Build data x, y
# data_x = [itm[1] for itm in data_list]
# data_y = [itm[0] for itm in data_list]

# print("data_x:",len(data_x))
# print("data_y:",len(data_y))
# print("data_x:",data_x[:5])
# print("data_y:",data_y[:5])


# test_percent = 0.10
# validation_percent = 0.2

# # Split data into train / test
# train_validate_x, test_x, train_validate_y, test_y = train_test_split(data_x, data_y, test_size=test_percent)

# # Split data into train / validate
# train_x, validate_x, train_y, validate_y = train_test_split(train_validate_x, train_validate_y, test_size=test_percent)

# print("train_x count:",len(train_x))
# print("validate_x count:",len(validate_x))
# print("test_x count:",len(test_x))

# image_width = 224
# image_height = 224
# num_channels = 3
# batch_size = 32

# train_shuffle_buffer_size= len(train_x)
# validation_shuffle_buffer_size= len(validate_x)

# # Load Image
# def load_image(path, label):
#   image = tf.io.read_file(path)
#   image = tf.image.decode_jpeg(image, channels=num_channels)
#   image = tf.image.resize(image, [image_height,image_width])
#   return image, label

# # Normalize pixels
# def normalize(image, label):
#   image = image/255
#   #image = keras.applications.mobilenet.preprocess_input(image)
#   return image, label

# # Convert all y labels to numbers
# train_processed_y = [label2index[label] for label in train_y]
# validate_processed_y = [label2index[label] for label in validate_y]
# test_processed_y = [label2index[label] for label in test_y]

# # Converts to y to binary class matrix (One-hot-encoded)
# train_processed_y = to_categorical(train_processed_y, num_classes=num_classes)
# validate_processed_y = to_categorical(validate_processed_y, num_classes=num_classes)
# test_processed_y = to_categorical(test_processed_y, num_classes=num_classes)

# # Create TF Dataset
# train_data = tf.data.Dataset.from_tensor_slices((train_x, train_processed_y))
# validation_data = tf.data.Dataset.from_tensor_slices((validate_x, validate_processed_y))
# test_data = tf.data.Dataset.from_tensor_slices((test_x, test_processed_y))

# #############
# # Train data
# #############
# # Apply all data processing logic
# train_data = train_data.shuffle(buffer_size=train_shuffle_buffer_size)
# train_data = train_data.map(load_image, num_parallel_calls=AUTOTUNE)
# train_data = train_data.map(normalize, num_parallel_calls=AUTOTUNE)
# train_data = train_data.batch(batch_size)
# train_data = train_data.prefetch(AUTOTUNE)

# ##################
# # Validation data
# ##################
# # Apply all data processing logic
# validation_data = validation_data.shuffle(buffer_size=validation_shuffle_buffer_size)
# validation_data = validation_data.map(load_image, num_parallel_calls=AUTOTUNE)
# validation_data = validation_data.map(normalize, num_parallel_calls=AUTOTUNE)
# validation_data = validation_data.batch(batch_size)
# validation_data = validation_data.prefetch(AUTOTUNE)

# ############
# # Test data
# ############
# # Apply all data processing logic
# test_data = test_data.map(load_image, num_parallel_calls=AUTOTUNE)
# test_data = test_data.map(normalize, num_parallel_calls=AUTOTUNE)
# test_data = test_data.batch(batch_size)
# test_data = test_data.prefetch(AUTOTUNE)

# print("train_data",train_data)
# print("validation_data",validation_data)
# print("test_data",test_data)

# Login into wandb
# wandb.login(key='697fbe205f5979b08fbf04cd8f8448515402ce5b')
# wandb.login(key='697fbe205f5979b08fbf04cd8f8448515402ce5b')
# wandb.init(project="mushroom-detection", entity="nish1710")

# Create an account in WandB and generate a key to replace this

# Build data x, y
data_x = [itm[1] for itm in data_list]
data_y = [itm[0] for itm in data_list]

print("data_x:",len(data_x))
print("data_y:",len(data_y))
print("data_x:",data_x[:5])
print("data_y:",data_y[:5])

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout, BatchNormalization
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.utils import to_categorical
from sklearn.model_selection import train_test_split

# Set constants
image_width = 224
image_height = 224
num_channels = 3
batch_size = 32
num_classes = 3  # Modify this based on your actual number of classes
test_percent = 0.10
validation_percent = 0.2

# Assuming your `data_x` and `data_y` are already defined
train_validate_x, test_x, train_validate_y, test_y = train_test_split(data_x, data_y, test_size=test_percent)
train_x, validate_x, train_y, validate_y = train_test_split(train_validate_x, train_validate_y, test_size=validation_percent)

# Convert labels to numerical format (e.g., one-hot encoding)
label2index = {'amanita': 0, 'crimini': 1, 'oyster': 2}  # Replace with your actual labels
train_processed_y = [label2index[label] for label in train_y]
validate_processed_y = [label2index[label] for label in validate_y]
test_processed_y = [label2index[label] for label in test_y]

train_processed_y = to_categorical(train_processed_y, num_classes=num_classes)
validate_processed_y = to_categorical(validate_processed_y, num_classes=num_classes)
test_processed_y = to_categorical(test_processed_y, num_classes=num_classes)

# Prepare the TensorFlow dataset
AUTOTUNE = tf.data.AUTOTUNE

# Load Image function
def load_image(path, label):
    image = tf.io.read_file(path)
    image = tf.image.decode_jpeg(image, channels=num_channels)
    image = tf.image.resize(image, [image_height, image_width])
    return image, label

# Normalize function
def normalize(image, label):
    image = image / 255.0  # Normalize to [0, 1]
    return image, label

# Create TF Datasets
train_data = tf.data.Dataset.from_tensor_slices((train_x, train_processed_y))
validation_data = tf.data.Dataset.from_tensor_slices((validate_x, validate_processed_y))
test_data = tf.data.Dataset.from_tensor_slices((test_x, test_processed_y))

# Train data processing
train_data = train_data.shuffle(buffer_size=len(train_x))
train_data = train_data.map(load_image, num_parallel_calls=AUTOTUNE)
train_data = train_data.map(normalize, num_parallel_calls=AUTOTUNE)
train_data = train_data.batch(batch_size)
train_data = train_data.prefetch(AUTOTUNE)

# Validation data processing
validation_data = validation_data.shuffle(buffer_size=len(validate_x))
validation_data = validation_data.map(load_image, num_parallel_calls=AUTOTUNE)
validation_data = validation_data.map(normalize, num_parallel_calls=AUTOTUNE)
validation_data = validation_data.batch(batch_size)
validation_data = validation_data.prefetch(AUTOTUNE)

# Test data processing
test_data = test_data.map(load_image, num_parallel_calls=AUTOTUNE)
test_data = test_data.map(normalize, num_parallel_calls=AUTOTUNE)
test_data = test_data.batch(batch_size)
test_data = test_data.prefetch(AUTOTUNE)

# Define the custom CNN model
model = Sequential([
    Conv2D(32, (3, 3), activation='relu', input_shape=(image_height, image_width, num_channels)),
    BatchNormalization(),
    MaxPooling2D(pool_size=(2, 2)),

    Conv2D(64, (3, 3), activation='relu'),
    BatchNormalization(),
    MaxPooling2D(pool_size=(2, 2)),

    Conv2D(128, (3, 3), activation='relu'),
    BatchNormalization(),
    MaxPooling2D(pool_size=(2, 2)),

    Flatten(),
    Dense(128, activation='relu'),
    Dropout(0.5),
    Dense(num_classes, activation='softmax')  # Softmax for multi-class classification
])

# Compile the model
model.compile(optimizer=Adam(learning_rate=0.001),
              loss='categorical_crossentropy',
              metrics=['accuracy'])

# Model summary
model.summary()

# Train the model
history = model.fit(
    train_data,
    validation_data=validation_data,
    epochs=20,
    verbose=1
)

# Evaluate the model on test data
test_loss, test_accuracy = model.evaluate(test_data)
print(f"Test Loss: {test_loss}")
print(f"Test Accuracy: {test_accuracy}")

# Save the model
model.save("custom_mushroom_model.h5")
print("Model saved as 'custom_mushroom_model.h5'")

import matplotlib.pyplot as plt

# Plot training & validation loss values
plt.figure(figsize=(12, 6))

plt.subplot(1, 2, 1)
plt.plot(history.history['loss'], label='train loss')
plt.plot(history.history['val_loss'], label='validation loss')
plt.title('Model Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()

# Plot training & validation accuracy values
plt.subplot(1, 2, 2)
plt.plot(history.history['accuracy'], label='train accuracy')
plt.plot(history.history['val_accuracy'], label='validation accuracy')
plt.title('Model Accuracy')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend()

plt.tight_layout()
plt.show()

"""**Here you can load your own image to to test out**

### Uncomment it and tweak it as per your needs
"""

import numpy as np
from tensorflow.keras.preprocessing import image

# Function to load and preprocess a new image
def prepare_image(image_path):
    img = image.load_img(image_path, target_size=(image_height, image_width))  # Resize image
    img_array = image.img_to_array(img)  # Convert to array
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
    img_array = img_array / 255.0  # Normalize to [0, 1]
    return img_array

# Predict the class of a new image
def predict_image(model, image_path):
    img_array = prepare_image(image_path)
    predictions = model.predict(img_array)
    predicted_class = np.argmax(predictions, axis=-1)  # Get index of highest probability
    return predicted_class

# # Test the prediction function
# image_path = '/content/photo-1571074635691-b910c7a5cdbb.jpeg'  # Replace with the actual image path
# predicted_class = predict_image(model, image_path)

# # Print the predicted class
# class_names = {'amanita': 0, 'crimini': 1, 'oyster': 2}   # Replace with your actual class names
# print(f"Predicted class: {class_names[predicted_class[0]]}")

# Test the prediction function
image_path = '/content/momBabyAmanita-fly-agaric-teaser-1200x628.jpg'  # Replace with the actual image path
predicted_class = predict_image(model, image_path)

# Print the predicted class
class_names = {0: 'amanita', 1: 'crimini', 2: 'oyster'}   # Invert the dictionary
#class_names = {'amanita': 0, 'crimini': 1, 'oyster': 2}   # Replace with your actual class names

# Get the predicted class name using the predicted class index
predicted_class_name = list(class_names.values())[predicted_class[0]]

# Print the prediction
print(f"Predicted class: {predicted_class_name}")