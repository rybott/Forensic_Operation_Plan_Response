import pandas as pd
from datetime import timedelta , datetime
import duckdb as ddb
import random

class CompanyGeneration:
  def __init__(self,RF, yera, product, yr_product_data):
    self.RF = RF
    self.year = yera
    self.yr_product_data = yr_product_data
    self.Sales_df = pd.DataFrame({"A":[1,2,3],"B":[4,5,6]})
    self.product = product

  def GenerateSales(self): # Already Per Product
    print(self.year)
    yr_Quantity_Sold = self.yr_product_data[self.yr_product_data['yr_Product']==self.product]['yr_Quantity_Sold'].item()
    Product_Cost = self.yr_product_data[self.yr_product_data['yr_Product']==self.product]['Product_Cost'].item()
    Selling_Price = self.yr_product_data[self.yr_product_data['yr_Product']==self.product]['Selling_Price'].item()
    MinRecords_PerInvoice = int(self.yr_product_data[self.yr_product_data['yr_Product']==self.product]['yr_noRecordsMin'])
    MaxRecords_PerInvoice = int(self.yr_product_data[self.yr_product_data['yr_Product']==self.product]['yr_noRecordsMax'])
    Vendor = self.yr_product_data[self.yr_product_data['yr_Product']==self.product]['Vendors'].item()

    # Initial Quantity
    Quantity_Remaining = yr_Quantity_Sold
    Yr_Start = datetime(self.year, 1, 1)
    Yr_End = datetime(self.year, 12, 31)

    Sales_df_rows = []
    x = 0

    while Quantity_Remaining > 0:
      Order_Date = Yr_Start + timedelta(days=random.randint(0, (Yr_End-Yr_Start).days))
      # Product is Shipped 1-30 days after order
      Shipment_Date = Order_Date + timedelta(days = random.randint(1, 30))
      Records_PerInvoice = random.randint(MinRecords_PerInvoice, MaxRecords_PerInvoice)
      if Records_PerInvoice > Quantity_Remaining:
        Records_PerInvoice = Quantity_Remaining
      else:
        pass
      Rev = Records_PerInvoice * Selling_Price
      Tcost = Records_PerInvoice * Product_Cost
      Sales_df_rows.append([self.product, Records_PerInvoice, Order_Date, Shipment_Date, Selling_Price, Product_Cost, Rev, Tcost, Vendor])
      Quantity_Remaining = Quantity_Remaining - Records_PerInvoice

      # Record Journal Entries for Rev and Cash or AR

    self.Sales_df = pd.DataFrame(Sales_df_rows, columns = ["Product", "Quantity",
                                                      "Order_Date", "Shipment_Date",
                                                      "Selling_Price", "Product_Cost",
                                                      "Rev", "Total_cost", "Vendors"])

    cleaned_df = self.Sales_df[['Shipment_Date', 'Rev']].copy()
    cleaned_df.rename(columns={'Shipment_Date': 'Date', 'Rev': 'Amount'}, inplace=True)
    self.RF.JournalEntries_Bulk(cleaned_df,1000,4000,"dr",1010,1000,70,30)
    # 1000 - Cash | 1010 - Accounts Payable | 4000 - Revenue

    print("Rev:",self.Sales_df['Rev'].sum())
    self.RF.Rev_Record(self.year, self.Sales_df['Rev'].sum())

    return [self.year, self.Sales_df]

  def GeneratePO(self, Master_Inventory):
    Sales_df = self.Sales_df
    Product_Ordered = []
    self.Quantity_Purchased = []
    self.Date_Purchased = []
    self.InventoryBeg = []
    self.InventoryEnd = []
    Vendor = []

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
      Beg_Inventory = Master_Inventory.ReadInventory(product)

      New_Inventory = Beg_Inventory - Quantity_Sold
      if New_Inventory <= 0:
        Purchase_Quantity  = Quantity_Sold * 1.05
        New_Inventory = Beg_Inventory + Quantity_Sold * .05
        # Update Master Inventory and Record PO
        Master_Inventory.UpdateInventory(product, New_Inventory)
        PO_row = [product, Quantity_Sold, Quantity_Sold*Product_Cost, Purchase_Date,Vendor, Beg_Inventory, New_Inventory]
        PO_rows.append(PO_row)
      else:
       Master_Inventory.UpdateInventory(product, New_Inventory)

    self.PO_df = pd.DataFrame(PO_rows, columns=['Product', 'Quantity_Sold', 'Cost', 'Purchase_Date', 'Vendor', 'Beg_Inventory', 'New_Inventory'])

    cleaned_df = self.PO_df[['Purchase_Date', 'Cost']].copy()
    cleaned_df.rename(columns={'Purchase_Date': 'Date', 'Cost': 'Amount'}, inplace=True)
    self.RF.JournalEntries_Bulk(cleaned_df,1010,2000)
    # 1010 - Inventory | 2000 - Accounts Payable (To be Paid in 30 days) | 1000 - Cash
    cleaned_df['Date'] += pd.Timedelta(days=30) # Date Payed
    self.RF.JournalEntries_Bulk(cleaned_df,2000,1000)

    return [self.year,self.PO_df]