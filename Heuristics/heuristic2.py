import pandas as pd
import os
import time
import operator
from operator import attrgetter
import traceback

csv = 'GoldenPlainsThirteenSat' #raw_input("Enter the name of the file to import: ")
df = pd.DataFrame()
#import csv of weights
df = pd.read_csv('{}.csv'.format(csv), index_col=0)

csv_two = 'GoldenPlainsThirteenSat-travel' #raw_input("Enter the name of the file to import (travel times): ")
travel = pd.DataFrame()
#import csv of travel
travel = pd.read_csv('{}.csv'.format(csv_two), index_col=0)

lookForward = 0
while ((lookForward < 2) or (lookForward > 4)):
    lookForward = 3 #input("Enter the number of periods to look forward (between 2 - 4): ")


numBreaks = 1 #input("Enter the number of breaks per a day: ")


### get the biggest weight from every column ###

#print travel
#print df

#Start Time
start_time =time.time()

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

##Create visual array -> basically outputArray
visualArray = []
for each in df.columns:
    visualArray.append(MyClass(0, "", each))

# Add columns equal to the number of possible look-forwards
totalCol = len(df.columns) + lookForward
while len(df.columns) < totalCol:
    df['A' + str(len(df.columns))] = pd.Series([0 for x in range(len(df.index))])

    
#print df  
    
    
# selection: https://stackoverflow.com/questions/14941097/selecting-pandas-column-by-location
# sum: https://stackoverflow.com/questions/25748683/pandas-sum-dataframe-rows-for-given-columns
#iterate through each row/column, choosing largest weight of 
#the sum of the number of periods we are looking forward
i = 0
for column in df:
    #df[df.columns[i]]
    ##Find relevant columns
    columnList = df.iloc[:, i:i+lookForward]
    #print columnList
    df[column].astype(float)
    #print "iteration", i
    try: 
        #select largest value in first column
        if (i==0):
            df.iloc[:,0].max
            outputArray[i].weight = df[column].max()
            outputArray[i].band = df[column].idxmax()
            outputArray[i].time = column
            visualArray[i].weight = df[column].max()
            visualArray[i].band = df[column].idxmax()
            visualArray[i].time = column
        elif (i>0):
            ##Create temporary dataframe for sum of column in each row
            #from https://stackoverflow.com/questions/34682828/extracting-specific-selected-columns-to-new-dataframe-as-a-copy
            dfTemp = pd.DataFrame()
            #print "column list", columnList
            dfTemp = columnList
            dfTemp['options'] = 0
            #dfTemp = df[columnList].sum(axis=1)

            ##Create options dictionary
            # sum, band, time
            options = {}

            ##Consider the options here
            ###Option 1: watch -> wait/watch -> wait/watch -> wait/watch###
            options['Stay'] = [dfTemp.loc[outputArray[i-1].band,:].sum(), outputArray[i-1].band, column]
            #print outputArray[i-1].band
            ###Option 2: travel -> watch -> watch -> watch###
            for index, row in dfTemp.iterrows():
                ##Consult travel matrix
                if (index != outputArray[i-1].band):
                    #print "this", travel.loc[index,outputArray[i-1].band]
                    if (travel.loc[index,outputArray[i-1].band] > 0):
                        #print index
                        #print column
                        #print dfTemp.loc[index, 'options']
                        #print "sum ", dfTemp.loc[index].sum(axis=0)
                        dfTemp.loc[index, column] = 0
                        dfTemp.loc[index, 'options'] = dfTemp.loc[index].sum(axis=0)
                    else:
                        dfTemp.loc[index, 'options'] = dfTemp.loc[index].sum(axis=0)
            ##Select Highest Option
            options['Travel-1'] = [dfTemp.loc[:,'options'].max(), dfTemp.loc[:,'options'].idxmax(),column]
            
            ##Select Overall Highest Option
            #from https://stackoverflow.com/questions/268272/getting-key-with-maximum-value-in-dictionary
            #print options
            #print max(options.iteritems(), key=operator.itemgetter(1))
            if (max(options.iteritems(), key=operator.itemgetter(1))[0] == 'Travel-1'):
                visualArray[i].band = 'Travel'
                visualArray[i].weight = 0
                outputArray[i].weight = 0
            else:
                visualArray[i].band = max(options.iteritems(), key=operator.itemgetter(1))[1][1]
                visualArray[i].weight = dfTemp.loc[max(options.iteritems(), key=operator.itemgetter(1))[1][1],column]
                outputArray[i].weight = dfTemp.loc[max(options.iteritems(), key=operator.itemgetter(1))[1][1],column]
            
            visualArray[i].time = max(options.iteritems(), key=operator.itemgetter(1))[1][2]
            outputArray[i].band = max(options.iteritems(), key=operator.itemgetter(1))[1][1]
            outputArray[i].time = max(options.iteritems(), key=operator.itemgetter(1))[1][2]
            #print "output", outputArray[i]
    except Exception:
        traceback.print_exc()
        pass
    i = i + 1
    
##Replace lowest values with breaks.
#if breaks < minbreaks, then loop through and create more
allBreaks =[]
currentBreaks = 0
for each in visualArray:
    if (each.band == 'Breaks'):
        currentBreaks = currentBreaks + 1
#increase breaks
while (currentBreaks < numBreaks):
    #from https://stackoverflow.com/questions/6085467/python-min-function-with-a-list-of-objects
    min_weight = min(visualArray,key=attrgetter('weight'))
    if (min_weight.band != 'Breaks' or 'Travel'):
        min_weight.band = 'Breaks'
        min_weight.weight = 0
        currentBreaks=currentBreaks + 1
    
# output results

##Schedule
print "Festival:", csv
score = 0
for column in visualArray:
    #print column.band, column.time, column.weight
    print "Time: ", column.time, " Band: ", column.band
    score = score + column.weight
##Time
timeprocessed = time.time() - start_time
print "Time to Process: ", timeprocessed
##Solution Score
print "Solution Score: ", score
