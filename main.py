
# Imports
import pandas as pd
import numpy as np
from datetime import timedelta
import random
import duckdb as ddb

# Further Analysis
import matplotlib.pyplot as plt
import plotly.express as px

# Import Scenario Modules
from ScenarioOne import Generate_Scenario_1


# Initial User Data
regions_data = {
    'StoreID': [1,2,3,4,5,6,7,8,9,10],
    'StoreName': ["StoreNY","StoreLA","StorePA","StoreKY","StoreWA","StoreDC","StoreFL","StoreAL","StoreTX","StoreMN",]
}
regions_df = pd.DataFrame(regions_data)


products_data = {
    'Product': ["Office Supplies","Vegetables","Fruits","Cosmetics","Cereal","Baby Food","Beverages","Snacks","Clothes","Household","Personal Care","Meat"],
    'Unit_Price': [651.21,154.06,9.33,437.2,205.7,255.28,47.45,152.58,109.28,668.27,81.73,421.89],
    'Unit_Cost': [524.96,90.93,6.92,263.33,117.11,159.42,31.79,97.44,35.84,502.54,56.67,364.69]
}
products_df = pd.DataFrame(products_data)
# Change Product type
product_types = ['Cereal', 'Snacks', 'Beverages', 'Baby Food', 'Meat', 'Fruits', 'Vegetables', 'Personal Care', 'Cosmetics', 'Household', 'Office Supplies', 'Clothes']


start_date = pd.Timestamp('2015-01-01')
end_date = pd.Timestamp('2018-12-31')
num_records = 1000


# Expenses - Min Max Touples
Expenses = {
    'Avg_NetProfit':(3,"Not used to calc net profit"),
    'Rent': (6,10),
    'Insurance': (2,4),
    'Wages': (15,20),
    'Ads': (6,8),
    'Taxes': (13, "A fixed amount")}

NumberOf_Ads = random.randrange(3,12)

# Other Assets

# Euipment - Asset
Euipment_Exp_AsPercentof_EBITA = .05
Equipment_Useful_Life = 20
Preprogram_Useful_Life = (10/20)
Preprgram_Accum_depr = (10/20)

# Equipment - Note
Note_Payment_Yrs = 20
Note_Interest_Yrly = .05 # Agreement is .05% on original note value every year.
Note_Payment_Remaining = (10/20)

# Run Program
Generate_Scenario_1(regions_df,products_df,start_date,end_date,num_records,Expenses,NumberOf_Ads,Euipment_Exp_AsPercentof_EBITA,Equipment_Useful_Life,Preprogram_Useful_Life,
                        Preprgram_Accum_depr,Note_Payment_Yrs,Note_Interest_Yrly,Note_Payment_Remaining)