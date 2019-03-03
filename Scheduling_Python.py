# -*- coding: utf-8 -*-
# http://www.gurobi.com/resources/seminars-and-videos/modeling-with-the-gurobi-python-interface
#git sync with master https://stackoverflow.com/a/16330001
from gurobipy import *
import pandas as pd
import numpy as np
import csv
import os
import time
#-----------------------------input-------------------------
dirname = os.path.dirname(__file__) +'/'  
s= 'FRIDAY_COACHELLA'
data = pd.read_csv("{}.csv".format(dirname+s))
jobs = data.iloc[:,0:1]
jobs=jobs.values
jobs=np.insert(jobs, 0, ['Breaks'], 0)
print(jobs)
OutputSQLdf = data.iloc[:,:]


data = data.iloc[:,1:]

print(data.iloc[0,1]) #rows columns


#show = data.iloc[:,0]
show = data.shape[0]

interval = data.shape[1]
start_time =time.time()
#interval =7
try:
# Create a new model (m is the variable)
    m = Model("Personal_Music_Festival")
    vars_tup = [(i, j) for i in range(show) for j in range(interval)]
    x = m.addVars(vars_tup, lb=+0, vtype=GRB.BINARY, name="show_attended")
    b = m.addVars(interval, lb=+0, vtype=GRB.BINARY, name="break_taken")
    m.update()

    #objective function
    m.setObjective( -quicksum(x[i,j] * data.iloc[i,j] for i in range(show) for j in range(interval)))
    
    #constraint 1 only one action (break/show) can be schdule can be schedule in one interval
    for j in range(interval):
        m.addConstr(quicksum(x[i,j] for i in range(show)) + b[j] == 1, "c1")
    #constraint 2 there should at least one break 
    m.addConstr(quicksum(b[j] for j in range(interval)) >= 1, "c2" )

    m.optimize()
    #print output results
    print('Sum of Weight:', -m.objVal)
    for v in m.getVars():
        print(v.varName, v.x)
    print ("--- %s seconds ---" % (time.time() - start_time))
    #--------------------output results to csv-----------------
    getOutputList = m.getVars()
    OutputList = []
    #a list to hold all results from gurobi
    for i in range(len(getOutputList)):
        OutputList.append(str(getOutputList[i]))
    
    # Get rid of excess texts generated by Gurobi    
    OutputList = [w.replace('gurobi.Var show_attended[','') for w in OutputList]
    OutputList = [w.replace('gurobi.Var break_taken[','') for w in OutputList]
    OutputList = [w.replace(']','') for w in OutputList]
    OutputList = [w.replace(' (value ',',') for w in OutputList]
    OutputList = [w.replace('<','') for w in OutputList]
    OutputList = [w.replace('>','') for w in OutputList]
    OutputList = [w.replace('-','') for w in OutputList]
    OutputList = [w.replace('.0','') for w in OutputList]
    OutputList = [w.replace(')','') for w in OutputList]

    
    #add values into weight array 
    outputnp=np.zeros([show, interval])
    for i in range(0,len(OutputList)-interval):
            outputnp[int(OutputList[i].split(',')[0]),int(OutputList[i].split(',')[1])] =OutputList[i].split(',')[2]
    #print (outputnp)
    
    #add break into break array
    outputbreak = np.zeros([1,interval])
    for i in range(len(OutputList)-interval,len(OutputList)):
            outputbreak[0,int(OutputList[i].split(',')[0])] =OutputList[i].split(',')[1]
    #print (outputbreak)
    
    
    #append break and list together
    #add a row into array https://stackoverflow.com/a/8298873
    outputnp=np.insert(outputnp, 0, outputbreak, 0)  
    #convert array that contains break into df
    #convert array to df https://stackoverflow.com/a/53816059
    dfoutput = pd.DataFrame(data=outputnp)
    #insert job names and 'break'
    #https://stackoverflow.com/a/18674915 insert a column with specific index
    dfoutput.insert(loc=0, column='Jobs', value=jobs)
   

    
    #print (dfoutput)
    
    dfoutput.to_csv('output.csv', index=False)

    #print(OutputList)

    
except GurobiError:
    print('Error reported')