import pandas as pd
import random
from datetime import timedelta
from datetime import datetime
import duckdb as ddb

from companygeneration import CompanyGeneration
from preprocessing import PreProcessing
from records import RecordingFunctions , Inventory_manager , Data_manager

# This is a sample of what a product sheet would look like
# ID for vendor will mean something such as type of product or payment type
product_df = pd.DataFrame({
    "ProductID": [1,2,3,4],
    "Product": ["eggs","wine","cheese","candles"],
    "Vendor": [3001, 3002, 3003, 3004],
    "Unit_Price": [3.20, 16.20, 5.20,20.5],
    "Unit_Cost": [1.20, 3.40, 2.10, 10],
    "Initial_Inventory": [0,0,0,0],
    "Spread":[.30, .50, .10, .10],
    "PerInvoiceRng_Min":[10,10,10,10],
    "PerInvoiceRng_Max":[20,20,20,20]
})

# This would all come in as JSON not created in Python
Initial_Year = 2010
YearsIn_Operation = 10
first_year_rev = 10000000
trend = .05
modjulation = .01

x = first_year_rev
y = Initial_Year
coin = (1,2)

list_years = []

for year in range(YearsIn_Operation):
  Revenue = x
  Year = y
  Trended = Revenue * (1+trend)
  direction = random.sample(coin,1)
  if direction == 1:
    Modjulated = Trended * (1+modjulation)
  else:
    Modjulated = Trended * (1-modjulation)
  list_year_item = [Year, round(Revenue,2)]
  list_years.append(list_year_item)
  x = Modjulated
  y = y+1

# This is what the Data would look like in JSON
rev_df = pd.DataFrame(list_years,columns=["Year","Rev"])


#--------------------------------------------------------------------------------


Yr_Product_dict = {}
General_Journal = pd.DataFrame(columns = ["Date","Account","Amount","Balance"])

File_Manager = Data_manager()
Recording_Functions = RecordingFunctions(File_Manager)

for yr in rev_df["Year"]:
  # Processing Products
  Year_Rev = rev_df[rev_df['Year']==yr].values.tolist()[0]
  Processed_Products = PreProcessing(product_df, yr, Year_Rev).ProductProcessing()
  yr_product_data = Processed_Products[1]
  Inventory_data = Processed_Products[2] # New Function will manage Inventory Level State
  Inv_Manager = Inventory_manager(Inventory_data)

  for product in yr_product_data['yr_Product'].unique():
    Generator = CompanyGeneration(Recording_Functions,yr, product, yr_product_data)
    Generator.GenerateSales()
    Generator.GeneratePO(Inv_Manager)
    break
  
  break