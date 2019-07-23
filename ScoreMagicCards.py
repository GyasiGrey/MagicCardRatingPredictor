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

#Build the vocabulary from Type
types = dataset.pop('Type')
names = dataset.pop('Name')
rules = dataset.pop('RulesText')

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

print(dataset)