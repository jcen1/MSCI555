# -*- coding: utf-8 -*-
# http://www.gurobi.com/resources/seminars-and-videos/modeling-with-the-gurobi-python-interface

from gurobipy import *
import pandas as pd
import mysql.connector
from sqlalchemy import create_engine
import pymysql
#-----------------------------SQL database connection-------------------------
mydb = mysql.connector.connect(
  host="us-cdbr-iron-east-03.cleardb.net",
  user="b1eee63deab066",
  passwd="b7ee47b2",
  db = "heroku_13ba31d0f0cf30a"
)

engine = create_engine("mysql+pymysql://b1eee63deab066:b7ee47b2@us-cdbr-iron-east-03.cleardb.net/heroku_13ba31d0f0cf30a")

# data input from MySQL Database: Predicted Enrollment data  
# https://stackoverflow.com/a/52919505
data = pd.read_sql("SELECT * FROM predicted_enroll", con=mydb)

# ----------------------------------------------------Scheduling Parameters----------------------------------------------------------

course = list(set(data['course_code'])) # ith course #can this be duplicated? yes it can
month = [i for i in range(1,25)] # jth month 1-24

I = len(course) # (loop number of courses from database - dynamic)
J = 24 # 24 months (2 years ahead)

# http://python.omics.wiki/data-structures/dictionary/multiple-keys
# {(tuple), value} https://stackoverflow.com/a/2407405 LAST Comment helps
demandtuple=list(zip(data['course_code'],data['index_month']))

# https://stackoverflow.com/a/209854 pairwire update
# Predicted Demand from Prediction Algorithm
D=dict(zip(demandtuple, data['enrollment']))

# data input from MySQL Database: Parameters input for Constraints
constdata =pd.read_sql("select distinct p.course_code,c.maximum_capacity, c.minimum_enrollment, c.course_fee, c.course_cost from predicted_enroll as p left join course c on p.course_code = c.course_code;", con=mydb)

# MaxC = maxCdata.set_index('course_code').T.to_dict('int') https://stackoverflow.com/a/26716774
# https://stackoverflow.com/a/17426500
# Maximum capacity of course
MaxC = pd.Series(constdata.maximum_capacity.values,index=constdata.course_code).to_dict()
'''
MaxC = {"CCMC": 700,
        "FONP": 500,
        "PSCB": 120,
        "PNON": 50,
        "IHPC": 50}
'''
# Minimum enrollment needed to offer course
minE= pd.Series(constdata.minimum_enrollment.values,index=constdata.course_code).to_dict()
'''
minE = {"CCMC": 6,
        "FONP": 6,
        "PSCB": 6,
        "PNON": 15,
        "IHPC": 15}
'''
# Fees of Course (Revenue +ve)
R= pd.Series(constdata.course_fee.values,index=constdata.course_code).to_dict()
'''
R = {"CCMC": 199,
     "FONP": 499,
     "PSCB": 599,
     "PNON": 449,
     "IHPC": 399}
'''
# Cost of Course (Cost -ve)
C= pd.Series(constdata.course_cost.values,index=constdata.course_code).to_dict()
'''
C = {"CCMC": 500,
     "FONP": 750,
     "PSCB": 5000,
     "PNON": 3000,
     "IHPC": 2000}
'''
#Panda DataFrame(df) to output to sql
columns = ['course_code' , '1' , '2' , '3', '4' , '5','6','7','8','9','10','11','12','13',
           '14','15','16','17','18','19','20','21','22','23','24']
OutputSQLdf = pd.DataFrame(columns = columns,index = course)
#OutputSQLdf.set_index('course_code')

# ----------------------------------------------------Gurobi Optimisation----------------------------------------------------------
try:
# Create a new model (m is the variable)
    m = Model("DeSouza_Scheduling")

# Create Decision Variable Offer Course i in Month j https://stackoverflow.com/a/52567112
# http://www.gurobi.com/pdfs/user-events/2017-frankfurt/Modeling-1.pdf Tutorial
    vars_tup = [(i, j) for i in course for j in month ]
    x = m.addVars(vars_tup, lb=+0, vtype=GRB.BINARY, name="course_offered")

# 1, if course i is offered in month j; 0, otherwise
    y = m.addVars(vars_tup, vtype=GRB.BINARY, name="binary_constraint")
    
# Gurobi process any pending model modifications
    m.update()

# Objective Function: Maximize(Total Revenue - Total Cost)
    m.setObjective( quicksum(x[i,j] * D[i,j] * R[i] for i in course for j in month) - 
                   quicksum(x[i,j] * C[i] for i in course for j in month), GRB.MAXIMIZE)

# 1. Constraint = Max number of course offerings (12 for now) per month
    for j in range(1, J+1):
       m.addConstr( quicksum(x[i,j] for i in course) <= 2, "c1")
    
# 2. Constraint = 1.10 * Max Capacity of course >= Predicted Enrollment
    for i in course:
        for j in range(1, J+1):
            m.addConstr( 1.10 * MaxC[i] * x[i,j] >= D[i,j] * y[i,j], "c2")

# 3. Constraint = Minimum Enrollment of course <= Predicted Enrollment
    for i in course:
        for j in range(1, J+1):
            m.addConstr( minE[i] * x[i,j] <= D[i,j] * y[i,j], "c3") 

# 4. Constraint = Cost of course <= Revenue of course
    for i in course:
        for j in range(1, J+1):
            m.addConstr( C[i] * x[i,j] <= D[i,j] * R[i], "c4") 

# Optimize model to obtain schedule
    m.optimize()
    
# Print Results
# Print which course to schedule
    
#    var_names = []
#    var_value = []
#
#    for var in m.getVars():
#        
#        var_names.append(var)
#    
#    print(var_names)
#    print(var_value)
#    
    #for i in range(len(var_names)):
      #  put them in a horizontal list and then use dataframe to upload one whole row .
       # use dataframe.loc[i]
    
#    for v in m.getVars():
#        print(v.varName, v.x)
    
    getOutputList = m.getVars()
    OutputList = []
    
    for i in range(len(getOutputList)):
        OutputList.append(str(getOutputList[i]))    
    
    
# Split by half, removing "Binary_constraint (y variables)" section
    OutputList = OutputList[:int(len(OutputList)/2)]
    
# Get rid of excess texts generated by Gurobi    
    OutputList = [w.replace('gurobi.Var course_offered[','') for w in OutputList]
    OutputList = [w.replace(']','') for w in OutputList]
    OutputList = [w.replace(' (value ',',') for w in OutputList]
    OutputList = [w.replace('<','') for w in OutputList]
    OutputList = [w.replace('>','') for w in OutputList]
    OutputList = [w.replace('-','') for w in OutputList]
    OutputList = [w.replace('.0','') for w in OutputList]
    OutputList = [w.replace(')','') for w in OutputList]

# https://stackoverflow.com/a/44534185 split
# Put data from List to DataFrame, prepping to export to database
    OutputSQLdf['course_code']= course
    for i in range(0,len(OutputList)):
        OutputSQLdf.at[OutputList[i].split(',')[0],OutputList[i].split(',')[1]] =OutputList[i].split(',')[2]
    print (OutputSQLdf)

# Output scheduling output to MySQL
    OutputSQLdf.to_sql('scheduling_output', engine, if_exists='replace',index =False)
# remove duplicate https://www.w3schools.com/python/python_howto_remove_duplicates.asp
# listindex = list(dict.fromkeys(listindex))
    
# Close database connectivity    
    mydb.close()

# Print objective value (Net Profit)
    print('Net Profit:', m.objVal)

# Gurobi Error-catching
except GurobiError:
    print('Error reported')
