import pandas as pd
from Generator_Func import * 
from Scenarios import *

# Changable Constants 
regions_data = {
    'StoreID': [1,2,3,4,5,6,7,8,9,10],
    'StoreName': ["StoreNY","StoreLA","StorePA","StoreKY","StoreWA","StoreDC","StoreFL","StoreAL","StoreTX","StoreMN",]
}
regions_df = pd.DataFrame(regions_data)

products_data = {
    'Product': ["Office Supplies","Vegetables","Fruits","Cosmetics","Cereal","Baby Food","Beverages","Snacks","Clothes","Household","Personal Care","Meat"],
    'Unit Price': [651.21,154.06,9.33,437.2,205.7,255.28,47.45,152.58,109.28,668.27,81.73,421.89],
    'Unit Cost': [524.96,90.93,6.92,263.33,117.11,159.42,31.79,97.44,35.84,502.54,56.67,364.69]
}
products_df = pd.DataFrame(products_data)
# Initial Inventory levels
Inventory_dict = {'Cereal':0, 'Snacks':0, 'Beverages':0, 'Baby Food':0, 'Meat':0, 'Fruits':0, 'Vegetables':0, 'Personal Care':0, 'Cosmetics':0, 'Household':0, 'Office Supplies':0, 'Clothes':0}
Vendor_dict = {'Cereal':'Foodco', 'Snacks':'Foodco', 'Beverages':'Foodco', 'Baby Food':'Foodco', 'Meat':'Farmco', 'Fruits':'Farmco', 'Vegetables':'Farmco', 'Personal Care':'Beautyco', 'Cosmetics':'Beautyco', 'Household':'Homeco', 'Office Supplies':'Homeco', 'Clothes':'Fashionco'}


start_date = pd.Timestamp('2020-01-01')
end_date = pd.Timestamp('2022-01-01')
num_records = 1000
# Change the dynamic of the buisness with max and min order quantities
Q1 = 1000 # Minimum per order
Q2 = 10000 # Maximum per order



# Company Generation
Sales = generate_sales_data(num_records, start_date, end_date, regions_df, products_df, Q1, Q2)
sales_df = generate_sales_data(num_records, start_date, end_date, regions_df, products_df, Q1, Q2)[0]
PO_df = generate_purchase_orders(sales_df,Vendor_dict,Inventory_dict,products_df)
Inventory = generate_Inventory(sales_df,PO_df)
Expenses = Scenario_1(Sales[1])


print(sales_df.info())
print(PO_df.info())
print(Inventory.info())