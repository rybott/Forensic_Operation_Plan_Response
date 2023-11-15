
# Imports
import pandas as pd
import random
import sqlite3 as sql

# Further Analysis
import matplotlib.pyplot as plt
import plotly.express as px

# Import Scenario Modules
from Scenario_1.S1_Generator import Generate_Scenario_1

# Create the temp Database 
conn = sql.connect('Company_Financials.db')


# Define all the atributes of your company here
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


Initial_Inventory_dict = {'Cereal':0, 'Snacks':0, 'Beverages':0, 'Baby Food':0, 'Meat':0, 'Fruits':0, 'Vegetables':0, 'Personal Care':0, 'Cosmetics':0, 'Household':0, 'Office Supplies':0, 'Clothes':0}


start_date = pd.Timestamp('2015-01-01')
end_date = pd.Timestamp('2018-12-31')
num_records = 1000 # Number of Sales randomized throughout the time period
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

# Run Program
Generate_Scenario_1(conn,
                    regions_df,
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
                    Initial_Inventory_dict,
                    Initial_Cash)