import pyodbc
import tensorflow as tf
import pandas as pd
from tensorflow import keras
from tensorflow.keras import layers

wordBag = {}
wordBag["<PAD>"] = 0
wordBag["<UNUSED>"] = 1

#Turns a string into a sequence of integers
def encode_text(text):
  result = []
  
  for token in text.split():
    result.append(wordBag[token])
    
  return result


#Get the Magic Card dataset from the SQL Database
sql_conn = pyodbc.connect('DRIVER={ODBC Driver 13 for SQL Server}; SERVER=localhost\SQLEXPRESS; DATABASE=MagicCards;Trusted_Connection=yes')
query = "SELECT Name, RulesText, CMC, Power, Toughness, Type, Rating FROM Cards"
dataset = pd.read_sql(query, sql_conn)

#Only include cards with a CMC of <= 20
#Because GleeMax HAS A CMC OF 1000000 AND IT THROWS OFF THE MATH COME ON GUYS.
dataset = dataset[dataset.CMC <= 20]


#Build the vocabulary from Type
types = dataset.pop('Type')
names = dataset.pop('Name')
rules = dataset.pop('RulesText')

#Changes all nones to 0.
#All power/toughness of NULL (All noncreature cards)
#All ratings of NULL
dataset.fillna(value=0, inplace=True)

#Convert the ratings to integers
ratings = dataset.pop('Rating') * 1000

#Re-add the ratings to the dataset
dataset["Rating"] = ratings.astype(int)

#Remove the emdash from types
types = types.str.replace(" — ", " ")

#Remove puncuation from rules text
rules = rules.str.replace(" — ", " ")
rules = rules.str.replace(",", "")
rules = rules.str.replace(".", "")
rules = rules.str.replace("(", "")
rules = rules.str.replace(")", "")

wordIndex = 10

#Add words from Types to the wordBag
for row in types.str.split():
  for token in row:
    wordBag[token] = wordIndex
    wordIndex += 1

#Add words from Names to the wordBag
for row in names.str.split():
  for token in row:
    wordBag[token] = wordIndex
    wordIndex += 1

#Add words from RulesText to the wordBag
for row in rules.str.split():
  if row is not None:
    for token in row:
      wordBag[token] = wordIndex
      wordIndex += 1

#Turn all the types to integers
typesInt = []
for row in types:
  typesInt.append(encode_text(row))

#Turn all the names to integers
namesInt = []
for row in names:
  namesInt.append(encode_text(row))

#Turn all the rules to integers
rulesInt = []
for row in rules:
  if row is None:
    unusedRow = []
    unusedRow.append(wordBag["<UNUSED>"])
    rulesInt.append(unusedRow)
  else:
    rulesInt.append(encode_text(row))

#Add the types as integers
dataset['Type'] = typesInt

#Add the names as integers
dataset['Name'] = namesInt

#Add the rules as integers
dataset['RulesText'] = rulesInt

#Split out the train and test data
train_dataset = dataset.sample(frac=0.8, random_state=0)
test_dataset = dataset.drop(train_dataset.index)

train_stats = train_dataset.describe()
train_stats.pop("Rating")
train_stats = train_stats.transpose()

#split the labels out
train_labels = train_dataset.pop('Rating')
test_labels = test_dataset.pop('Rating')


#normalize the data
def norm(x):
  return (x - train_stats['mean']) / train_stats['std']

#OH NO: no normed data  
#normed_train_data = norm(train_dataset)
#normed_test_data = norm(test_dataset)


#build the model
def build_model():
  model = keras.Sequential([
    layers.Dense(64, activation=tf.nn.relu, input_shape=[len(train_dataset.keys())]),
    layers.Dense(64, activation=tf.nn.relu),
    layers.Dense(1)
  ])
  
  optimizer = tf.keras.optimizers.RMSprop(0.001)
  
  model.compile(loss='mean_squared_error', optimizer=optimizer, metrics=['mean_absolute_error', 'mean_squared_error'])
  
  return model
  
model = build_model()

EPOCHS = 1000

class PrintDot(keras.callbacks.Callback):
  def on_epoch_end(self, epoch, logs):
    if epoch % 100 == 0: print('')
    print('.', end='')


#Stop early
early_stop = keras.callbacks.EarlyStopping(monitor='val_loss', patience=10)

#history = model.fit(normed_train_data, train_labels, epochs=EPOCHS, validation_split = 0.2, verbose = 0, callbacks=[early_stop, PrintDot()])
history = model.fit(train_dataset, train_labels, epochs=EPOCHS, validation_split = 0.2, verbose = 0, callbacks=[early_stop, PrintDot()])



example_batch = train_dataset[:10]
example_result = model.predict(example_batch)




hist = pd.DataFrame(history.history)
hist['epoch'] = history.epoch

#test_predictions = model.predict(normed_test_data).flatten()
test_predictions = model.predict(test_dataset).flatten()

#loss, mae, mse = model.evaluate(normed_test_data, test_labels, verbose = 0)
loss, mae, mse = model.evaluate(test_dataset, test_labels, verbose = 0)

print("Testing set Mean Abs Error: {:5.2f}".format(mae))

print("Labels")
print(test_labels)

print("Predictions")
print(test_predictions)