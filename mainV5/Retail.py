import pandas as pd
from datetime import timedelta, datetime
import duckdb as ddb
import random

class Retail:
  def __init__(self, Records, yrly_Data, Inv_manager):
    self.records = Records
    self.Yearly_Data = yrly_Data
    self.Inventory_manager = Inv_manager

  def GenerateSales(self):
    PO_df_rows = []
    Sales_df_rows = []
    for yr in self.Yearly_Data['Year'].unique():
      yr_data = self.Yearly_Data[self.Yearly_Data['Year']==yr].copy()
      for product in yr_data['Product'].unique():
        product_data = yr_data[yr_data['Product']==product].copy()
        Quantity_Remaining = product_data['q_sold']
        Yr_Start = datetime(yr, 1, 1)
        Yr_End = datetime(yr, 1, 1)
        Product_Cost = product_data['Unit_Cost']
        Selling_Price = product_data['Unit_Price']
        MinRecords = product_data['PerInvoiceRng_Min']
        MaxRecords = product_data['PerInvoiceRng_Max']

        while Quantity_Remaining > 0:
          Order_Date = Yr_Start + timedelta(days=random.randint(0, (Yr_End-Yr_Start).days))
          # Product is Shipped 1-30 days after order
          Shipment_Date = Order_Date + timedelta(days = random.randint(1, 30))
          Records_PerInvoice = random.randint(MinRecords, MaxRecords)
          if Records_PerInvoice > Quantity_Remaining:
            Records_PerInvoice = Quantity_Remaining
          else:
            pass
          Rev = Records_PerInvoice * Selling_Price
          Tcost = Records_PerInvoice * Product_Cost
          Sales_df_rows.append([yr, product, Records_PerInvoice, Order_Date, Shipment_Date, Selling_Price, Product_Cost, Rev, Tcost])
          Quantity_Remaining = Quantity_Remaining - Records_PerInvoice


    self.Sales_df = pd.DataFrame(Sales_df_rows, columns = ["Year","Product", "Quantity",
                                                        "Order_Date", "Shipment_Date",
                                                        "Selling_Price", "Product_Cost",
                                                        "Rev", "Total_cost", "Vendors"])
    cleaned_df = self.Sales_df[['Shipment_Date', 'Rev']].copy()
    cleaned_df.rename(columns={'Shipment_Date': 'Date', 'Rev': 'Amount'}, inplace=True)
    self.RF.JournalEntries_Bulk(cleaned_df,1000,4000,"dr",1010,1000,70,30)
    # 1000 - Cash | 1010 - Accounts Payable | 4000 - Revenue
    

  def GeneratePOs(self):
    for yr in self.Sales_df['Year'].unique():
      yr_data = self.Sales_df[self.Sales_df['Year']==yr].copy()
      for product in yr_data['Product'].unique():
        product_data = yr_data[yr_data['Product'] == product].copy()
        Beg_Inventory = self.Inventory_manager.ReadInventory(product)

        qry_PO = '''
        SELECT Vendors AS Vendor,
        Product,
        SUM(Quantity) AS Quantity,
        Product_Cost,
        YEAR(Order_Date) as Year,
        QUARTER(Order_Date) as Quarter,
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
        FROM Sales_df
        GROUP BY Vendor, Product,Product_Cost, YEAR(Order_Date), Quarter(Order_Date)
        ORDER BY Purchase_Date
        '''

        df_PO = ddb.sql(qry_PO).df()
        PO_rows = []
        for index, row in df_PO.iterrows():
          product = row['Product']
          Quantity_Sold = row['Quantity']
          Product_Cost = row['Product_Cost']
          Vendor = row['Vendor']
          Purchase_Date = row['Purchase_Date']
          Beg_Inventory = self.Inventory_manager.ReadInventory(product)

          New_Inventory = Beg_Inventory - Quantity_Sold
          if New_Inventory <= 0:
            Purchase_Quantity  = Quantity_Sold * 1.05
            New_Inventory = Beg_Inventory + Quantity_Sold * .05
            # Update Master Inventory and Record PO
            self.Inventory_manager.UpdateInventory(product, New_Inventory)
            PO_row = [yr, product, Quantity_Sold, Quantity_Sold*Product_Cost, Purchase_Date,Vendor, Beg_Inventory, New_Inventory]
            PO_rows.append(PO_row)
          else:
            self.Inventory_manager.UpdateInventory(product, New_Inventory)

    self.PO_df = pd.DataFrame(PO_rows, columns=['Year','Product', 'Quantity_Sold', 'Cost', 'Purchase_Date', 'Vendor', 'Beg_Inventory', 'New_Inventory'])

    cleaned_df = self.PO_df[['Purchase_Date', 'Cost']].copy()
    cleaned_df.rename(columns={'Purchase_Date': 'Date', 'Cost': 'Amount'}, inplace=True)
    self.RF.JournalEntries_Bulk(cleaned_df,1010,2000)
    # 1010 - Inventory | 2000 - Accounts Payable (To be Paid in 30 days) | 1000 - Cash
    cleaned_df['Date'] += pd.Timedelta(days=30) # Date Payed
    self.RF.JournalEntries_Bulk(cleaned_df,2000,1000)

    return [self.PO_df]

  def Generate_Retail(self):
    Sales = Retail.GenerateSales()
    PO = Retail.GeneratePOs()
    print(Sales.info())
    print(PO.info())