import pandas as pd
# input for numbers
# raw_input for words

csv = raw_input("Enter the name of the file to import: ")
df = pd.DataFrame()
#dji = pd.read_excel("Assignment 3&4-data files/{}.xlsx".format('DJI-daily'), skiprows=22,usecols=[0, 1],index_col=0)



### get the biggest weight from every column ###

#import csv of weights
df = pd.read_csv('{}.csv'.format(csv), index_col=0)

#From https://stackoverflow.com/questions/51136283/pandas-insert-empty-row-at-0th-position
#Add a row of zeros
df.loc[len(df)] = 0
#Shift everything down
df = df.shift()
#Make top row zeros
df.loc[0] = 0

print df

# create object containing (Weight,Band,Time)
class MyClass(object):
    def __init__(self, weight, band, time):
        self.weight = weight
        self.band = band
        self.time = time

# find length of dataFrame (the width in this case)
# create array of length of data
outputArray = []
for each in df.columns:
    outputArray.append(MyClass(0, "", each))

#iterate through each row/column, choosing largest weight
#put weight in an array of objects containing (Weight,Band,Time)
i = 0
for column in df:
    #print(df[column])
    #print outputArray[i]
    df[column].astype(float)
    outputArray[i].weight = df[column].max()
    outputArray[i].band = df[column].idxmax()
    outputArray[i].time = column
    i = i + 1

# output results
#print [column.time for column in outputArray]
#print [column.band for column in outputArray]

for column in outputArray:
    print "Time: ", column.time, " Band: ", column.band