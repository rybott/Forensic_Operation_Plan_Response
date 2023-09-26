import pandas as pd
import numpy as np
from datetime import timedelta
import random
import duckdb as ddb

def generate_sales_data(num_records, start_date, end_date, regions_df, products_df, Q1, Q2):
    # Lists to store generated data
    order_dates = []
    shipment_dates = []
    regions = []
    countries = []
    product_types = []
    unit_prices = []
    unit_costs = []
    quantities = []

    # Generate data for each record
    for _ in range(num_records):
        # Randomly select region and corresponding country
        region_row = regions_df.sample().iloc[0]
        regions.append(region_row['StoreID'])
        countries.append(region_row['StoreName'])

        # Randomly select product and corresponding unit price and cost
        product_row = products_df.sample().iloc[0]
        product_types.append(product_row['Product'])
        unit_prices.append(product_row['Unit Price'])
        unit_costs.append(product_row['Unit Cost'])

        # Random order date between start and end date
        random_date = start_date + timedelta(days=np.random.randint(0, (end_date-start_date).days))
        order_dates.append(random_date)
        # Ship date between 1 and 50 days after order date
        shipment_dates.append(random_date + timedelta(days=np.random.randint(1, 51)))

        # Random quantity between 1000 and 10000
        quantities.append(np.random.randint(Q1, Q2))

    # Create dataframe
    sales_df = pd.DataFrame({
        'Order_Date': order_dates,
        'Shipment_Date': shipment_dates,
        'StoreID': regions,
        'StoreName': countries,
        'Product_Type': product_types,
        'Unit_Price': unit_prices,
        'Unit_Cost': unit_costs,
        'Quantity': quantities,
        'Revenue': np.array(unit_prices) * np.array(quantities),
        'Total_Cost': np.array(unit_costs) * np.array(quantities)})

    # Total Revenue Per year
    qry_Trev = '''
        SELECT YEAR(Shipment_Date) AS Year, SUM(Revenue) AS Revenue
        FROM sales_df
        GROUP BY Year
        Order By Year
    '''

    # Total Revenue Per Product Per year
    qry_rev = '''
        SELECT YEAR(Shipment_Date) AS Year, Product_Type AS Product, SUM(Revenue) AS Revenue
        FROM sales_df
        GROUP BY Year, Product
        Order By Year
    '''

    df_Trev = ddb.sql(qry_Trev).df()
    df_rev = ddb.sql(qry_rev).df()

    
    Rev_dict = dict(zip(df_Trev['Year'],df_Trev['Revenue'])) 


    return [sales_df,Rev_dict]

def generate_purchase_orders(sales_data, Vendor_dict, Inventory_dict, products_df):
    sales_data = sales_data.sort_values(by=['Order_Date'])
    purchase_orders = pd.DataFrame(columns=['OrderID', 'Product', 'Vendor', 'Quantity', 'OrderDate'])
    Product_Ordered = []
    Quantity_Purchased = []
    Date_Purchased = []
    Vendor = []

    for index, row in sales_data.iterrows():
        x = 0
        product = row['Product_Type']
        quantity_sold = row['Quantity']
        order_date = row['Order_Date']
        Unit_Cost = row['Unit_Cost']

        if product in Inventory_dict.keys():
            if quantity_sold > Inventory_dict[product]:
                purchase_quantity = (quantity_sold - Inventory_dict[product]) * 1.05
                Inventory_dict[product] = (purchase_quantity + Inventory_dict[product]) - quantity_sold
                Product_Ordered.append(product)
                Quantity_Purchased.append(purchase_quantity)
                Date_Purchased.append(order_date)
                Ven = Vendor_dict[product]
                Vendor.append(Ven)
        else:
            Inventory_dict[product] = Inventory_dict[product] - quantity_sold

    PO_df = pd.DataFrame(
        {'Vendor': Vendor,
        'Quantity': Quantity_Purchased,
        'Product': Product_Ordered,
        'Order_Date': Date_Purchased,
        'Unit_Cost': Unit_Cost
        })

    Qry_PO ='''
        SELECT Vendor,
        Product,
        SUM(Quantity),
        YEAR(Order_Date) AS Year,
        QUARTER(Order_Date) AS Quarter,
        CAST(
        CASE
            WHEN QUARTER(Order_Date) = 1
            THEN CONCAT(YEAR(Order_Date), '-01-01')
            WHEN QUARTER(Order_Date) = 2
            THEN CONCAT(YEAR(Order_Date), '-04-01')
            WHEN QUARTER(Order_Date) = 3
            THEN CONCAT(YEAR(Order_Date), '-07-01')
            WHEN QUARTER(Order_Date) = 4
            THEN CONCAT(YEAR(Order_Date), '-10-01')
        END AS DATE) AS Purchase_Date
        FROM PO_df
        GROUP BY Vendor, Product, YEAR(Order_Date), QUARTER(Order_Date)
        ORDER BY Year, Quarter
    '''

    df_PO = ddb.sql(Qry_PO).df()

    df_PO = df_PO.merge(products_df[['Product','Unit Cost']], on ='Product', how = 'left')

    return df_PO

def generate_Inventory(sales_df, PO_df):
    Inv_DEC = pd.DataFrame({"Date" : sales_df['Order_Date'],"Product":sales_df["Product_Type"],"Quantity":sales_df["Quantity"],"Unit_Cost":sales_df["Unit_Cost"]})
    Inv_INC = pd.DataFrame({"Date": PO_df['Purchase_Date'],"Product":PO_df['Product'],"Quantity":PO_df['sum(Quantity)'],"Unit_Cost":PO_df["Unit Cost"],"Vendor":PO_df['Vendor']})
    INV_df = Inv_DEC.append(Inv_INC,ignore_index=True)

    return INV_df

