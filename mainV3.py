# Imports
import pandas as pd
import random
import sqlite3 as sql
import time

# Further Analysis
import matplotlib.pyplot as plt
import plotly.express as px

# Import Scenario Modules
from Scenario_1.S1_GeneratorV3 import Generate_Scenario_12
from Scenario_1.S1_Fraud import Generate_Fraud1

# Create the temp Database 
conn = sql.connect('Company_Financials.db')

stores_df = pd.DataFrame({
    'StoreID': [1,2,3,4,5,6,7,8, 9,10],
    'StoreName': ["StoreNY","StoreLA","StorePA","StoreKY","StoreWA","StoreDC","StoreFL","StoreAL","StoreTX","StoreMN",]
})

products_df = pd.DataFrame({
    'ProductID':[420,421,234,565,875,987,568,676,456,675,984,547],
    'Product': ['Cereal', 'Snacks', 'Beverages', 'Baby Food', 'Meat', 'Fruits', 'Vegetables', 'Personal Care', 'Cosmetics', 'Household', 'Office Supplies', 'Clothes'],
    'Vendor': ['Foodco','Foodco','Foodco','Foodco','Farmco','Farmco','Farmco','Beautyco','Beautyco','Homeco','Homeco','Fashionco'],
    'Unit_Price': [651.21,154.06,9.33,437.2,205.7,255.28,47.45,152.58,109.28,668.27,81.73,421.89],
    'Unit_Cost': [524.96,90.93,6.92,263.33,117.11,159.42,31.79,97.44,35.84,502.54,56.67,364.69],
    'Initial_Inventory': [0,0,0,0,0,0,0,0,0,0,0,0]
})

start_date = pd.Timestamp('2018-01-01')
end_date = pd.Timestamp('2023-12-31')
num_records = 100000 # Number of Sales randomized throughout the time period with 10 Seconds per 1000 records
items_per_order = (1000,10001) # Insert both a min and max numbers of items in a single order (All orders contain just one type of product)


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
Preprogram_Useful_Life_Remaining = (10/20)

# Equipment - Note
Note_Payment_Yrs = 20
Note_Interest_Yrly = .05 # Agreement is .05% on original note value every year.
Note_Payment_Remaining = (10/20)

# Initial Cash Flow to make sure their are funds in the beginning of the time period for costs. 
Initial_Cash = 40000000

start_time = time.time()

Clean_Journal = Generate_Scenario_12(conn, 
                        stores_df,
                        products_df,
                        start_date,
                        end_date,
                        num_records,
                        items_per_order,
                        Expenses,
                        NumberOf_Ads,
                        Euipment_Exp_AsPercentof_EBITA,
                        Equipment_Useful_Life,
                        Preprogram_Useful_Life_Remaining,
                        Note_Payment_Yrs,
                        Note_Interest_Yrly,
                        Note_Payment_Remaining,
                        Initial_Cash)

print("Finished Generating")
section_1_time = time.time() - start_time
print("Time taken for Generating: {:.2f} seconds".format(section_1_time))

Fstart_date = pd.Timestamp('2017-01-01')
Fend_date = pd.Timestamp('2017-12-31')
num_Frecords = 100

start_time = time.time()

Generate_Fraud1(conn,Clean_Journal,stores_df,products_df,Fstart_date,Fend_date,num_Frecords)

print("Finished Fraud Generating")
section_1_time = time.time() - start_time
print("Time taken for Generating: {:.2f} seconds".format(section_1_time))