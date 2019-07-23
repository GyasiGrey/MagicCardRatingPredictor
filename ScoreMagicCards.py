import pyodbc
import tensorflow as tf
import pandas as pd
from tensorflow import keras
from tensorflow.keras import layers

#Get the Magic Card dataset from the SQL Database
sql_conn = pyodbc.connect('DRIVER={ODBC Driver 13 for SQL Server}; SERVER=localhost\SQLEXPRESS; DATABASE=MagicCards;Trusted_Connection=yes')
query = "SELECT CardId, Name, RulesText, CMC, Power, Toughness, Type, Rating FROM Cards"
dataset = pd.read_sql(query, sql_conn)

#Build the vocabulary from Type
types = dataset.pop('Type')

#Remove the emdash
types = types.str.replace(" — ", " ")

print(types)
#types_bow = {}

#for token in types.str.split():
#  types_bow[token] = 1

#sorted(types_bow.items())

#df = pd.DataFrame(pdf.Series(dict([(token, 1) for token in dataset['RulesText'].split()])), columns=['sent']).T