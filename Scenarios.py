'''
This File contains all of the different scenarios that can be called by the user in the main file
'''
import random
import pandas as pd

Exp_dict = {}
Exp_list = []

def Scenario_1(Rev_dict):

    Expenses = {
        'COGS': (45,55),
        'Rent': (6,10),
        'Insurance': (2,4),
        'Wages': (15,20),
        'Ads': (6,8)}

    for year in Rev_dict.keys():
        Rev = Rev_dict[year]
        Year = year
        COGS = (random.randrange(Expenses['COGS'][0],Expenses['COGS'][1])/100)*Rev
        Rent = (random.randrange(Expenses['Rent'][0],Expenses['Rent'][1])/100)*Rev
        Insurance = (random.randrange(Expenses['Insurance'][0],Expenses['Insurance'][1])/100)*Rev
        Wages = (random.randrange(Expenses['Wages'][0],Expenses['Wages'][1])/100)*Rev
        Ads = (random.randrange(Expenses['Wages'][0],Expenses['Wages'][1])/100)*Rev
        PM = Rev - (COGS+Rent+Insurance+Wages+Ads)
        Exp_dict = {'Year':Year,'Rev':Rev,'COGS':COGS,'Rent':Rent,'Insurance':Insurance,'Wages':Wages,'Ads':Ads,'Profit_Margin':PM}
        Exp_list.append(Exp_dict)

    Exp_df = pd.DataFrame(Exp_list)

    return Exp_df
    
