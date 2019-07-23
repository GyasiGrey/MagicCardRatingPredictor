import tensorflow as tf
import pandas as pd
from tensorflow import keras
from tensorflow.keras import layers

#Get the Magic Card dataset
column_names = ['CardId', 'Name', 'RulesText', 'CMC', 'Power', 'Toughness', 'Type', 'MultiverseId', 'Rating']
raw_dataset = pd.read_csv('MagicCards.csv', names=column_names, na_values = "?", comment='\t', sep=",", skipinitialspace=True, skiprows=1, encoding='utf-8')

dataset = raw_dataset.copy()


#Drop unknown rows
dataset = dataset.dropna()

#Toss the MultiverseId column
dataset.pop('MultiverseId')

print(dataset['RulesText'].split())

#df = pd.DataFrame(pdf.Series(dict([(token, 1) for token in dataset['RulesText'].split()])), columns=['sent']).T