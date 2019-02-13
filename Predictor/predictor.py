#usr/bin/python

#from __future__import absolute_import, division, print_function

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

import pathlib
import csv
import os

if(os.path.isfile('./pi.csv') != True):
	print("You need a file named pi.csv in the current directory to run")
	quit()

print("Welcome to the predictor")


  


column_names = ['Priority', 'Emergency_num', 'Hospital_num', 'Distance_Away', 'Since_Epoch',
			'Time_to_inc', 'Time_to_dest', 'Year', 'Year_day', 'Month', 'Week_day', 'Hour']

raw_dataset = pd.read_csv("./pi.csv", names = column_names, sep=",", header = 0)
dataset = raw_dataset.copy()
dataset.tail()

dataset = dataset.dropna()
dataset = dataset.drop(dataset[dataset.Hospital_num != 1].index) # remove all that are not going to Overlake

train_dataset = dataset.sample(frac=0.8, random_state=0)
test_dataset = dataset.drop(train_dataset.index)

show_initial_graphs = input("Do you want to see the graph of the variables, 1 = yes: ")
sns.set(style="ticks", color_codes=True)
if(show_initial_graphs == "1"):
	sns.pairplot(train_dataset[["Priority", "Distance_Away", "Time_to_inc", "Hour"]], diag_kind="kde")#,
		#vars = ["Priority", "Day_of_Year"])
	plt.show()

train_labels = train_dataset.pop('Priority')
test_labels = test_dataset.pop('Priority')

train_stats = train_dataset.describe()
#train_stats.pop('Priority')
train_stats = train_stats.transpose()
def norm(x):
	return (x - train_stats['mean']) / train_stats['std']

normed_train_data = norm(train_dataset)
normed_test_data  = norm(test_dataset)

#sns.pairplot(train_dataset, diag_kind="kde")

def build_model():
  model = keras.Sequential([
    layers.Dense(64, activation=tf.nn.relu, input_shape=[len(train_dataset.keys())]),
    layers.Dense(64, activation=tf.nn.relu),
    layers.Dense(1)
  ])
  optimizer = tf.keras.optimizers.RMSprop(0.001)
  model.compile(loss='mse',
                optimizer=optimizer,
                metrics=['mae', 'mse'])
  return model  


model = build_model()

class PrintDot(keras.callbacks.Callback):
  def on_epoch_end(self, epoch, logs):
    if epoch % 100 == 0: print('')
    print('.', end='')


#history will be where we keep the validation of the training
EPOCHS = 100

history = model.fit(
	normed_train_data, train_labels, epochs = EPOCHS, 
	validation_split = 0.2, verbose = 0, callbacks=[PrintDot()])

hist = pd.DataFrame(history.history)
hist['epoch'] = history.epoch
hist.tail()

print(hist)
print(history)

def plot_history(history):
  hist = pd.DataFrame(history.history)
  hist['epoch'] = history.epoch
  
  plt.figure()
  plt.xlabel('Epoch')
  plt.ylabel('Mean Abs Error [Priority]')
  plt.plot(hist['epoch'], hist['mean_absolute_error'],
           label='Train Error')
  plt.plot(hist['epoch'], hist['val_mean_absolute_error'],
           label = 'Val Error')
  plt.legend()
  plt.ylim([0,5])
  
  plt.figure()
  plt.xlabel('Epoch')
  plt.ylabel('Mean Square Error [$Priority^2$]')
  plt.plot(hist['epoch'], hist['mean_squared_error'],
           label='Train Error')
  plt.plot(hist['epoch'], hist['val_mean_squared_error'],
           label = 'Val Error')
  plt.legend()
  plt.ylim([0,20])

plot_history(history)

model = build_model()

# The patience parameter is the amount of epochs to check for improvement
early_stop = keras.callbacks.EarlyStopping(monitor='val_loss', patience=10)

history = model.fit(normed_train_data, train_labels, epochs=EPOCHS,
                    validation_split = 0.2, verbose=0, callbacks=[early_stop, PrintDot()])



plot_history(history)
plt.show()

loss, mae, mse = model.evaluate(normed_test_data, test_labels, verbose=0)

test_predictions = model.predict(normed_test_data).flatten()

plt.scatter(test_labels, test_predictions)
plt.xlabel('True Values [Priority]')
plt.ylabel('Predictions [Priority]')
plt.axis('equal')
plt.axis('square')
plt.xlim([0,plt.xlim()[1]])
plt.ylim([0,plt.ylim()[1]])
_ = plt.plot([-100, 100], [-100, 100])


error = test_predictions - test_labels
plt.hist(error, bins = 25)
plt.xlabel("Prediction Error [Priority]")
_ = plt.ylabel("Count")




print("Testing set Mean Abs Error: {:5.2f} Priority".format(mae))




print("End of predictor")


