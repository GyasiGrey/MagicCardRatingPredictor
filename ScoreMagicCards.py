import pyodbc
import tensorflow as tf
import pandas as pd
from tensorflow import keras
from tensorflow.keras import layers

wordBag = {}

#Turns a string into a sequence of integers
def encode_text(text):
  result = []
  
  for token in text.split():
    result.append(wordBag[token])
    
  return result


#Get the Magic Card dataset from the SQL Database
sql_conn = pyodbc.connect('DRIVER={ODBC Driver 13 for SQL Server}; SERVER=localhost\SQLEXPRESS; DATABASE=MagicCards;Trusted_Connection=yes')
query = "SELECT CardId, Name, RulesText, CMC, Power, Toughness, Type, Rating FROM Cards"
dataset = pd.read_sql(query, sql_conn)

#Build the vocabulary from Type
types = dataset.pop('Type')

#Remove the emdash
types = types.str.replace(" — ", " ")

wordIndex = 10

for row in types.str.split():
  for token in row:
    wordBag[token] = wordIndex
    wordIndex += 1

typesInt = []
#Turn all the types to integers
for row in types:
  typesInt.append(encode_text(row))

#Add the types as integers
dataset['Type'] = typesInt

print(dataset)