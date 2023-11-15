# Import for
import pandas as pd
import numpy as np
from datetime import timedelta
import random
import duckdb as ddb
import sqlite3 as sql

# Further Analysis
import matplotlib.pyplot as plt
import plotly.express as px


def Generate_Scenario_1(conn, 
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
                        Preprogram_Useful_Life,
                        Note_Payment_Yrs,
                        Note_Interest_Yrly,
                        Note_Payment_Remaining,
                        Initial_Inventory_dict,
                        Initial_Cash):
  
  Start_Year = start_date.strftime('%Y')
  End_Year = int(end_date.strftime('%Y'))
#------------------ Generate Sales Data -------------------------------#
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

      region_row = regions_df.sample().iloc[0]
      regions.append(region_row['StoreID'])
      countries.append(region_row['StoreName'])

      # Randomly select product and corresponding unit price and cost
      product_row = products_df.sample().iloc[0]
      product_types.append(product_row['Product'])
      unit_prices.append(product_row['Unit_Price'])
      unit_costs.append(product_row['Unit_Cost'])

      # Random order date between start and end date
      random_date = start_date + timedelta(days=np.random.randint(0, (end_date-start_date).days))
      order_dates.append(random_date)
      # Ship date between 1 and 50 days after order date
      shipment_dates.append(random_date + timedelta(days=np.random.randint(1, 51)))

      # Random quantity between 1000 and 10000
      quantities.append(np.random.randint(items_per_order[0], items_per_order[1]))

  # Initial Inventory Levels
  Inventory_dict = Initial_Inventory_dict.copy()
  Vendor_dict = {'Cereal':'Foodco', 'Snacks':'Foodco', 'Beverages':'Foodco', 'Baby Food':'Foodco', 'Meat':'Farmco', 'Fruits':'Farmco', 'Vegetables':'Farmco', 'Personal Care':'Beautyco', 'Cosmetics':'Beautyco', 'Household':'Homeco', 'Office Supplies':'Homeco', 'Clothes':'Fashionco'}

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
      'Total_Cost': np.array(unit_costs) * np.array(quantities)
  })

  sales_df['Total Profit'] = sales_df['Revenue'] - sales_df['Total_Cost']

#-----------------------------Purchase Orders----------------------------#

  purchase_orders = pd.DataFrame(columns=['OrderID', 'Product', 'Vendor', 'Quantity', 'OrderDate'])

  Product_Ordered = []
  Quantity_Purchased = []
  Date_Purchased = []
  InventoryBeg = []
  InventoryEnd = []
  Vendor = []
  Quantity_Sold = []

  for index, row in sales_df.iterrows():
    x = 0
    product = row['Product_Type']
    quantity_sold = row['Quantity']
    order_date = row['Order_Date']
    Unit_Cost = row['Unit_Cost']

    if product in Inventory_dict.keys():

      '''
      You can also insert here a new table of externalities that effect COGS or price delta logic
      '''
      InventoryBeg.append(Inventory_dict[product])
      Quantity_Sold.append(quantity_sold * -1)

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

      InventoryEnd.append(Inventory_dict[product])



  PoInv_df = pd.DataFrame(
      {'Order_Date': Date_Purchased,
      'Vendor': Vendor,
      'Quantity': Quantity_Purchased,
      'Product': Product_Ordered,
      'InventoryBeg': InventoryBeg,
      'InventoryEnd': InventoryEnd,
      'Quantity)Sold': Quantity_Sold,
      })

  Qry_PO ='''
      SELECT Vendor,
      Product,
      SUM(Quantity) AS Quantity,
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
      FROM PoInv_df
      GROUP BY Vendor, Product, YEAR(Order_Date), QUARTER(Order_Date)
      ORDER BY Year, Quarter
  '''

  df_PO = ddb.sql(Qry_PO).df()

  df_PO = df_PO.merge(products_df[['Product','Unit_Cost']], on ='Product', how = 'left')


#-----------------------------Total Revenue Calculations---------------#

  # Total Revenue
  qry_Trev = '''
      SELECT YEAR(Shipment_Date) AS Year, SUM(Revenue) AS Revenue
      FROM sales_df
      GROUP BY Year
      Order By Year
  '''

  # Total Revenue Per Product Per year
  qry_rev = '''
      SELECT YEAR(Shipment_Date) AS Year, Product_Type AS Product, SUM(Revenue) AS Revenue, Unit_Cost
      FROM sales_df
      GROUP BY Year, Product, Unit_Cost
      Order By Year
  '''

  df_Trev = ddb.sql(qry_Trev).df()
  # df_rev = ddb.sql(qry_rev).df()

  Rev_dict = dict(zip(df_Trev['Year'],df_Trev['Revenue']))

#----------------------------------COGS-------------------------#

  # COGS Quantities = Beg Inventory + Purchases - End Inventory
  PoInv_df['COGS_Quantity'] =  PoInv_df['InventoryBeg'] + PoInv_df['Quantity'] - PoInv_df['InventoryEnd']

  # Add the unit costs (This could be where you add more sophisticated logic for price changes)
  PoInv_df = PoInv_df.merge(products_df[['Product','Unit_Cost']], on ='Product', how = 'left')

  COGS_df1 = PoInv_df[['Order_Date','Product','COGS_Quantity','Unit_Cost']]

  COGS_qry1 = '''
      SELECT
        CAST(
          CASE
            WHEN Quarter(Order_Date) = 1
              THEN CONCAT(YEAR(Order_Date), '-01-30')
            WHEN Quarter(Order_Date) = 2
              THEN CONCAT(YEAR(Order_Date), '-04-30')
            WHEN Quarter(Order_Date) = 3
              THEN CONCAT(YEAR(Order_Date), '-07-30')
            WHEN Quarter(Order_Date) = 4
              THEN CONCAT(YEAR(Order_Date), '-10-30')
          END
          AS DATE) AS Date,
        Product,
        SUM((COGS_Quantity * Unit_Cost)) AS Value
      FROM COGS_df1
      GROUP BY Date, Product
    ORDER BY Date
  '''
  COGS_df_byProduct = ddb.sql(COGS_qry1).df()

  COGS_qry2 = '''
      SELECT Date, SUM(Value) AS Value
      FROM COGS_df_byProduct
      GROUP BY Date
      ORDER BY Date
  '''

  COGS_df = ddb.sql(COGS_qry2).df()

  # Gross Margin
  #   Yearly Rev - Yearly COGS
  # Yearly COGS

  Yr_COGS_qry = '''
      SELECT
          YEAR(Date) AS Year,
          Sum(Value) AS Value
      FROM COGS_df
      GROUP BY Year
  '''
  COGSyr_df = ddb.sql(Yr_COGS_qry).df()
  COGS_dict = dict(zip(COGSyr_df['Year'],COGSyr_df['Value']))

  PRC_dict = {}
  PM_dict = {}
  # Substract COGS from Rev each year
  for Year in Rev_dict.keys():
    try:
      PRC_dict[Year] = {"Rev":Rev_dict[Year],"COGS":COGS_dict[Year],"PM":Rev_dict[Year]-COGS_dict[Year]}
      PM_dict[Year] = Rev_dict[Year]-COGS_dict[Year]
    except:
      PRC_dict[Year] = {"Rev":Rev_dict[Year],"COGS":0,"PM":0}
      PM_dict[Year] = 0
  PM_Rev_df = pd.DataFrame({'PM':PM_dict,'REV':Rev_dict})


#--------------------------Expenses--------------------------#

  Expenses = {
      'Avg_NetProfit':(3,"Not used to calc net profit"),
      'Rent': (6,10),
      'Insurance': (2,4),
      'Wages': (15,20),
      'Ads': (6,8),
      'Taxes': (13, "A fixed amount")
  }

  Exp_dict = {}
  Exp_list = []

  for i, year in enumerate(PRC_dict.keys()):
      gross = PRC_dict[year]["PM"]
      Rev = PRC_dict[year]["Rev"]
      COGS = PRC_dict[year]["COGS"]
      Year = year


      Rent = (random.randrange(Expenses['Rent'][0],Expenses['Rent'][1])/100)*gross
      Insurance = (random.randrange(Expenses['Insurance'][0],Expenses['Insurance'][1])/100)*gross
      Wages = (random.randrange(Expenses['Wages'][0],Expenses['Wages'][1])/100)*gross
      Ads = (random.randrange(Expenses['Wages'][0],Expenses['Wages'][1])/100)*gross
      Net = gross - (Rent+Insurance+Wages+Ads)
      EBIT = (1 - (Expenses['Taxes'][0]/100)) * Net
      Tax = (Expenses['Taxes'][0]/100) * Net
      Net_In = EBIT - Tax

      Exp_dict = {'Year':Year,'Rev':Rev,'COGS':COGS,'Gross_Profit':gross,'Rent':Rent,'Insurance':Insurance,'Wages':Wages,'Ads':Ads,'Net_Profit':Net,'EBIT': EBIT, 'Taxes':Tax, 'Net_Income': Net_In}
      Exp_list.append(Exp_dict)


  Exp_df = pd.DataFrame(Exp_list)

  num_years = len(Exp_df['Year'])
  num_months = num_years*12

  rent = Exp_df['Rent'].sum() / num_months
  Insurance = Exp_df['Insurance'].sum() / num_months
  Wages = Exp_df['Wages'].sum() / num_months

  end_year_str = str(end_date)[:4]

  # Struct of List - Year, Date, Amount, Description
  Comp_Exp_List = []


  for year in Exp_df['Year']:
    if int(year) <= int(end_year_str):

      # Rent
      for month in range(12):
        Year = year
        Date = f"{Year}-1-{month+1}"
        Amount = rent
        Description = "Rent"
        sub_dict = {'Year':Year, 'Date':Date, 'Amount':Amount, 'Description':Description}
        Comp_Exp_List.append(sub_dict)

      # Insurance
      for month in range(12):
        Year = year
        Date = f"{Year}-1-{month+1}"
        Amount = Insurance
        Description = "Insurance"
        sub_dict = {'Year':Year, 'Date':Date, 'Amount':Amount, 'Description':Description}
        Comp_Exp_List.append(sub_dict)

      # Wages
      for month in range(12):
        Year = year
        Date = f"{Year}-1-{month+1}" # in the future it can be twice a month for 2 week pay
        Amount = Wages
        Description = "Wages"
        sub_dict = {'Year':Year, 'Date':Date, 'Amount':Amount, 'Description':Description}
        Comp_Exp_List.append(sub_dict)

      # Ads
      # Determine how many expenses per year
      No_Ads = NumberOf_Ads
      Ad_yrly = Exp_df[Exp_df['Year'] == year]['Ads'].iloc[0]
      amounts = []
      adj_amounts = []
      days = []
      months = []

      for ad in range(No_Ads):
        # Chose Random Days for Each Expense, you the same for each other random expense
        Day = random.randrange(1,28)
        month = random.randrange(1,12)
        amount = random.randint(1,100)
        amounts.append(amount)
        days.append(Day)
        months.append(month)

      amount_total = sum(amounts)

      for amount in amounts:
        amount = (amount/amount_total)*Ad_yrly
        adj_amounts.append(amount)

      for month, day, amount in zip(months,days,adj_amounts):
        Year = year
        Date =f"{Year}-1-{month}"
        Amount = amount
        Description = "Ads"
        sub_dict = {'Year':Year, 'Date':Date, 'Amount':Amount, 'Description':Description}
        Comp_Exp_List.append(sub_dict)
    else:
      pass

  Comp_Exp_df = pd.DataFrame(Comp_Exp_List)
  Comp_Exp_df['Date'] = pd.to_datetime(Comp_Exp_df['Date'],format='%Y-%m-%d')


#------------------------------Journals-------------------------#
  Account = []
  Date = []
  Description = []
  Amount = []
  Dr_Cr = []

  Gen_Journal_df = pd.DataFrame({
      'Account':Account,
      'Date':Date,
      'Description': Description,
      'Amount':Amount,
      'Dr_Cr':Dr_Cr})

#---------------------------Sales Journals----------------------#

  Accounts = []
  Dates = []
  Descriptions = []
  Amounts = []
  Dr_Crs = []
  ID = 0


  for index, row in sales_df.iterrows():
    ID = ID + 1
    date = row['Shipment_Date']
    amount = row['Revenue']
    desc = f"{ID}_Sale of Inventory "
    COGS = row['Total_Cost']
    Cash_acc = 1000
    AR_acc = 1010
    Rev_acc = 4000
    COGS_acc = 5000
    INV_acc = 1100

    rand_acc = random.randint(1,100)
    if rand_acc < 70:
      Sale_acc = AR_acc
    else:
      Sale_acc = Cash_acc

    # Sale
    Accounts.append(Sale_acc)
    Dates.append(date)
    Descriptions.append(desc)
    Amounts.append(amount)
    Dr_Cr = "Debit"
    Dr_Crs.append(Dr_Cr)

    Accounts.append(Rev_acc)
    Dates.append(date)
    Descriptions.append(desc)
    Amounts.append(amount)
    Dr_Cr = "Credit"
    Dr_Crs.append(Dr_Cr)


  Sales_Journal_df = pd.DataFrame({
      'Account':Accounts,
      'Date':Dates,
      'Description': Descriptions,
      'Amount':Amounts,
      'Dr_Cr':Dr_Crs})

  Gen_Journal_df = pd.concat([Gen_Journal_df,Sales_Journal_df], ignore_index=True)

#-------------------------------Purchase Order Journal----------------#

  Accounts = []
  Dates = []
  Descriptions = []
  Amounts = []
  Dr_Crs = []
  ID = 0


  for index, row in df_PO.iterrows():
    ID = ID + 1
    date = row['Purchase_Date']
    amount = row['Unit_Cost']*row['Quantity']
    desc = f"{ID}_Purchase of Inventory "
    AP_acc = 2000
    INV_acc = 1100

    Accounts.append(INV_acc)
    Dates.append(date)
    Descriptions.append(desc)
    Amounts.append(amount)
    Dr_Cr = "Debit"
    Dr_Crs.append(Dr_Cr)

    Accounts.append(AP_acc)
    Dates.append(date)
    Descriptions.append(desc)
    Amounts.append(amount)
    Dr_Cr = "Credit"
    Dr_Crs.append(Dr_Cr)


  Inventory_Journal_df = pd.DataFrame({
      'Account':Accounts,
      'Date':Dates,
      'Description': Descriptions,
      'Amount':Amounts,
      'Dr_Cr':Dr_Crs})

  Gen_Journal_df = pd.concat([Gen_Journal_df,Inventory_Journal_df,], ignore_index=True)

#-------------------------COGS Journal---------------------------#

  Accounts = []
  Dates = []
  Descriptions = []
  Amounts = []
  Dr_Crs = []
  ID = 0

  for index, row in COGS_df.iterrows():
    ID = ID + 1

    date = row['Date']
    amount = row['Value']
    desc = f"{ID}_Quarterly COGS"
    COGS = 5000
    INV_acc = 1100

    Accounts.append(COGS)
    Dates.append(date)
    Descriptions.append(desc)
    Amounts.append(amount)
    Dr_Cr = "Debit"
    Dr_Crs.append(Dr_Cr)

    Accounts.append(INV_acc)
    Dates.append(date)
    Descriptions.append(desc)
    Amounts.append(amount)
    Dr_Cr = "Credit"
    Dr_Crs.append(Dr_Cr)


  COGS_Journal_df = pd.DataFrame({
      'Account':Accounts,
      'Date':Dates,
      'Description': Descriptions,
      'Amount':Amounts,
      'Dr_Cr':Dr_Crs})

  Gen_Journal_df = pd.concat([Gen_Journal_df,COGS_Journal_df,], ignore_index=True)

#--------------------------------Expense Journal-----------------------#

  Accounts = []
  Dates = []
  Descriptions = []
  Amounts = []
  Dr_Crs = []
  ID = 0

  for index, row in Comp_Exp_df.iterrows():
    ID = ID + 1
    date = row['Date']
    amount = row['Amount']
    exp = row['Description']
    desc = f"{ID}_{exp} Expense"
    AP_acc = 2000
    Cash_acc = 1000

    match exp:
      # Fixed Cost Prepaid Exps are being accrued
      case 'Rent':
        account = 5110
        pay_acc = Cash_acc

      case 'Wages':
        account = 5010
        pay_acc = Cash_acc

      case 'Insurance':
        account = 5050
        pay_acc = Cash_acc

      case 'Ads':
        account = 5020
        rand_acc = random.randint(1,100)
        if rand_acc < 70:
          pay_acc = AP_acc
        else:
          pay_acc = Cash_acc

    Accounts.append(account)
    Dates.append(date)
    Descriptions.append(desc)
    Amounts.append(amount)
    Dr_Cr = "Debit"
    Dr_Crs.append(Dr_Cr)

    Accounts.append(pay_acc)
    Dates.append(date)
    Descriptions.append(desc)
    Amounts.append(amount)
    Dr_Cr = "Credit"
    Dr_Crs.append(Dr_Cr)

  Exp_Journal_df = pd.DataFrame({
    'Account':Accounts,
    'Date':Dates,
    'Description': Descriptions,
    'Amount':Amounts,
    'Dr_Cr':Dr_Crs})

  Gen_Journal_df = pd.concat([Gen_Journal_df,Exp_Journal_df,], ignore_index=True)

  Gen_Journal_df['Date'] = pd.to_datetime(Gen_Journal_df['Date'],format='%d-%m-%Y')

#------------------Paying Off AP and Recievables------------------#

  Accounts = []
  Dates = []
  Descriptions = []
  Amounts = []
  Dr_Crs = []

  for index, row in Gen_Journal_df.iterrows():
      # AP = 2000
      if row['Account'] == 2000:
          Purchase_date = row['Date']
          # All AP is Net 30 terms and we way in 30 days
          Cash_Paid_Date = row['Date'] + timedelta(days=30)
          Cash_Acc = 1000
          AP_Acc = 2000
          desc = "Paided down AP liability"
          amount = row["Amount"]

          Accounts.append(AP_Acc)
          Dates.append(Cash_Paid_Date)
          Descriptions.append(desc)
          Amounts.append(amount)
          Dr_Cr = "Debit"
          Dr_Crs.append(Dr_Cr)

          Accounts.append(Cash_Acc)
          Dates.append(Cash_Paid_Date)
          Descriptions.append(desc)
          Amounts.append(amount)
          Dr_Cr = "Credit"
          Dr_Crs.append(Dr_Cr)

      # AR = 1010
      elif row['Account'] == 1010:
          Purchase_date = row['Date']
          # All AP is Net 30 terms and we way in 30 days
          Days_Since_Paid = random.randint(5,100)
          Cash_Paid_Date = row['Date'] + timedelta(days=Days_Since_Paid)
          Cash_Acc = 1000
          AR_Acc = 1010
          desc = f"Recieved Recievables after {Days_Since_Paid} late"
          amount = row["Amount"]

          Accounts.append(Cash_Acc)
          Dates.append(Cash_Paid_Date)
          Descriptions.append(desc)
          Amounts.append(amount)
          Dr_Cr = "Debit"
          Dr_Crs.append(Dr_Cr)

          Accounts.append(AR_Acc)
          Dates.append(Cash_Paid_Date)
          Descriptions.append(desc)
          Amounts.append(amount)
          Dr_Cr = "Credit"
          Dr_Crs.append(Dr_Cr)

      else:
          pass

  AP_AR_Journal_df = pd.DataFrame({
  'Account':Accounts,
  'Date':Dates,
  'Description': Descriptions,
  'Amount':Amounts,
  'Dr_Cr':Dr_Crs})

  Gen_Journal_df = pd.concat([Gen_Journal_df,AP_AR_Journal_df,], ignore_index=True)

#--------- Calculating Retained Earnings from T Accounts --------------------#

  # Step 1
  qry_Tacc1 = '''
    SELECT
      Account,
      Date,
      CASE
          WHEN Dr_Cr = 'Credit'
            THEN Amount * -1
          WHEN Dr_Cr = 'Debit'
            THEN Amount
      END AS Amount
    FROM Gen_Journal_df
  '''
  Tacc1 = ddb.sql(qry_Tacc1).df()


  # Step 2
  qry_Tacc2 = '''
    SELECT
      Account,
      YEAR(Date) AS Year,
      ROUND(SUM(Amount),2) AS Amount
    FROM Tacc1
    GROUP BY Account, Year
    ORDER BY Year, Account
  '''
  Tacc2 = ddb.sql(qry_Tacc2).df()

  Tacc2_filtered = Tacc2[Tacc2['Year'] <= End_Year]
  def calculate_ebita(row):
      if row['Account'] == 4000 or row['Account'] == 5000:
          return row['Amount']
      elif row['Account'] in [5110, 5050, 5010, 5020]:
          return row['Amount']
      else:
          return 0
  Tacc2_filtered['EBITA'] = Tacc2_filtered.apply(calculate_ebita, axis=1)

  unadjusted_retained_earnings = Tacc2_filtered.groupby('Year')['EBITA'].sum().reset_index()

#----------- Adding Other Assets and Liabilities ----------------------#


  # Calculating Depreciation
  Test_EBITA = []
  Equipment_depr = []
  Years_list = []
  Unadjusted_RetainedEarnings = []

  for year in unadjusted_retained_earnings['Year']:
    # Unadjusted Retained Earnings = EBITA || Retained Earnings = Net Income calced now
    EBITA = unadjusted_retained_earnings.loc[(unadjusted_retained_earnings['Year'] == year), 'EBITA'].sum()
    Test_EBITA.append(EBITA)
    equipment_depr = EBITA * Euipment_Exp_AsPercentof_EBITA
    Equipment_depr.append(equipment_depr)
    Years_list.append(year)
    Unadjusted_RetainedEarnings.append(EBITA)

  Yearly_Equipment_depr = sum(Equipment_depr) / len(Equipment_depr) *-1


  # 20 and 30 Year useful life respectfully
  Value_Equipment_New = Yearly_Equipment_depr * Equipment_Useful_Life

  Accounts = []
  Dates = []
  Descriptions = []
  Amounts = []
  Dr_Crs = []
  RetainedEarnings = []

  # Scenario 1 - All assets will be 10 years into their book values
  # This variables will be the counters for depreciation
  Value_Equipment = Value_Equipment_New * Preprogram_Useful_Life # Half useful life remaining
  Value_Equipment_depr = Value_Equipment_New - Value_Equipment # Half Depreciated

  # Notes will be fixed 5% interest for 20 years for equipment
  Original_Notes = Value_Equipment_New
  # I can seperate them into monthly payments another day

  Note_Payments_Yearly = Original_Notes / Note_Payment_Yrs # Years of notes
  Interest_Payments_Yearly = Original_Notes * Note_Interest_Yrly


  Notes_Remaining = Original_Notes *Note_Payment_Remaining # 10 years of payments already done
  Notes_Counter = Notes_Remaining

  # Here we are adding depreciation notes payable and retained earnings to the additional journal
  for year in unadjusted_retained_earnings['Year']:
    if Value_Equipment != 0:
        Date = f"{year}-12-31"

      # Debit Depr Exp
        Accounts.append(5030)
        Dates.append(Date)
        Descriptions.append("Deprecation of Equipment")
        Amounts.append(Yearly_Equipment_depr)
        Dr_Cr = "Debit"
        Dr_Crs.append(Dr_Cr)

      # Credit depr - Equipment
        Accounts.append(1231)
        Dates.append(Date)
        Descriptions.append("Deprecation of Equipment")
        Amounts.append(Yearly_Equipment_depr)
        Dr_Cr = "Credit"
        Dr_Crs.append(Dr_Cr)

        Value_Equipment = Value_Equipment - Yearly_Equipment_depr
    else:
      pass

    if Notes_Counter != 0:
        Date = f"{year}-12-31"

      # Debit Notes Payable
        Accounts.append(2020)
        Dates.append(Date)
        Descriptions.append("Notes Payment")
        Amounts.append(Yearly_Equipment_depr*-1)
        Dr_Cr = "Debit"
        Dr_Crs.append(Dr_Cr)

      # Debit Interest Exp
        Accounts.append(5080)
        Dates.append(Date)
        Descriptions.append("Interest on Notes")
        Amounts.append(Interest_Payments_Yearly)
        Dr_Cr = "Debit"
        Dr_Crs.append(Dr_Cr)

      # Credit Cash
        Accounts.append(1000)
        Dates.append(Date)
        Descriptions.append("Notes/Interest Payment")
        Amounts.append(Interest_Payments_Yearly+Note_Payments_Yearly)
        Dr_Cr = "Credit"
        Dr_Crs.append(Dr_Cr)

        Notes_Counter = Notes_Counter - Note_Payments_Yearly
    else:
      pass

  # Finally we add the inital values carried over for Notes Payable and Equipment and inventory if applicable

  # Credit Notes Payable
  Accounts.append(2020)
  Dates.append(f"{Start_Year}-01-01")
  Descriptions.append("Initial Note")
  Amounts.append(Notes_Remaining *-1) # A removed -1
  Dr_Cr = "Credit"
  Dr_Crs.append(Dr_Cr)

  # Credit depr - Equipment
  Accounts.append(1231)
  Dates.append(f"{Start_Year}-01-01")
  Descriptions.append("Initial Accum Depr - Equip")
  Amounts.append(Value_Equipment_depr) # B Added -1
  Dr_Cr = "Credit"
  Dr_Crs.append(Dr_Cr)

  # Debit Equipment
  Accounts.append(1230)
  Dates.append(f"{Start_Year}-01-01")
  Descriptions.append("Initial Equipment")
  Amounts.append(Value_Equipment_New)
  Dr_Cr = "Debit"
  Dr_Crs.append(Dr_Cr)

  # This is an inflow of Cash to make sure nothing is negative

  # Debit Cash
  Accounts.append(1000)
  Dates.append(f"{Start_Year}-01-01")
  Descriptions.append("Cash From Last Year")
  Amounts.append(Initial_Cash)
  Dr_Cr = "Debit"
  Dr_Crs.append(Dr_Cr)

  # Credit Retained Earnings
  Accounts.append(3010)
  Dates.append(f"{Start_Year}-01-01")
  Descriptions.append("Cash From Last Year")
  Amounts.append(Initial_Cash)
  Dr_Cr = "Credit"
  Dr_Crs.append(Dr_Cr)

  # This logic is to balance retained earnings if initial inventory isn't zero
  if sum(Initial_Inventory_dict.values()) == 0:
    pass
  else:
    # Debit Inventory 
    Accounts.append(1100)
    Dates.append(f"{Start_Year}-01-01")
    Descriptions.append("Inventory From Last Year")
    Amounts.append(sum(Initial_Inventory_dict.values()))
    Dr_Cr = "Debit"
    Dr_Crs.append(Dr_Cr)

    # Credit Retained Earnings
    Accounts.append(3010)
    Dates.append(f"{Start_Year}-01-01")
    Descriptions.append("Inventory From Last Year")
    Amounts.append(sum(Initial_Inventory_dict.values()))
    Dr_Cr = "Credit"
    Dr_Crs.append(Dr_Cr)

  


  Additional_Journal_df = pd.DataFrame({
  'Account':Accounts,
  'Date':Dates,
  'Description': Descriptions,
  'Amount':Amounts,
  'Dr_Cr':Dr_Crs})

  Gen_Journal_df2 = pd.concat([Gen_Journal_df,Additional_Journal_df], ignore_index=True)
  Gen_Journal_df2['Date'] = pd.to_datetime(Gen_Journal_df2['Date'])


  Gen_Journal_df2['Date'] = Gen_Journal_df2['Date'].dt.strftime('%Y-%m-%d %H:%M:%S')

#------------------------------- Creating T accounts ----------#
  # Step 1
  qry_Tacc1_adjusted = '''
    SELECT
      Account,
      Date,
      CASE
          WHEN Dr_Cr = 'Credit'
            THEN Amount * -1
          WHEN Dr_Cr = 'Debit'
            THEN Amount
      END AS Amount
    FROM Gen_Journal_df2
  '''
  Tacc1_adjusted = ddb.sql(qry_Tacc1_adjusted).df()

  # Step 2
  qry_Tacc2_adjusted = '''
    SELECT
      Account,
      YEAR(CAST(Date AS DATE)) AS Year,  -- Casting the Date column to DATE
      ROUND(SUM(Amount),2) AS Amount
    FROM Tacc1_adjusted
    GROUP BY Account, YEAR(CAST(Date AS DATE))  -- Casting here as well for the GROUP BY clause
    ORDER BY Year, Account
  '''
  Tacc2_adjusted = ddb.sql(qry_Tacc2_adjusted).df()

#----------------------------Income Statments-----------------------#

  Year = []
  Sales_Rev = []
  COGS = []
  Gross_Profit = []
  Rent_exp = []
  Insurance_exp = []
  Salaries_exp = []
  Ad_exp = []
  Total_Operating_exp = []
  EBITA = []
  Interest_exp = []
  Depreciation_exp = []
  Income_Before_Tax = []
  Income_Tax = []
  Net_Income = []


  for year in Tacc2_adjusted['Year'].unique():
    if year <= End_Year:
      Year.append(year)
      sales_rev = Tacc2_adjusted.loc[(Tacc2_adjusted['Account']==4000) & (Tacc2_adjusted['Year']==year),'Amount'].iloc[0] * -1
      Sales_Rev.append(sales_rev)
      cogs = Tacc2_adjusted.loc[(Tacc2_adjusted['Account']==5000) & (Tacc2_adjusted['Year']==year),'Amount'].iloc[0]
      COGS.append(cogs)
      gross_profit = sales_rev - cogs
      Gross_Profit.append(gross_profit)
      rent_exp = Tacc2_adjusted.loc[(Tacc2_adjusted['Account']==5110) & (Tacc2_adjusted['Year']==year),'Amount'].iloc[0]
      Rent_exp.append(rent_exp)
      insurance_exp = Tacc2_adjusted.loc[(Tacc2_adjusted['Account']==5050) & (Tacc2_adjusted['Year']==year),'Amount'].iloc[0]
      Insurance_exp.append(insurance_exp)
      salaries_exp = Tacc2_adjusted.loc[(Tacc2_adjusted['Account']==5010) & (Tacc2_adjusted['Year']==year),'Amount'].iloc[0]
      Salaries_exp.append(salaries_exp)
      ad_exp = Tacc2_adjusted.loc[(Tacc2_adjusted['Account']==5020) & (Tacc2_adjusted['Year']==year),'Amount'].iloc[0]
      Ad_exp.append(ad_exp)
      total_op_exp = salaries_exp + insurance_exp + rent_exp + ad_exp
      Total_Operating_exp.append(total_op_exp)
      EBITA.append(gross_profit - total_op_exp)
      interest_exp = Tacc2_adjusted.loc[(Tacc2_adjusted['Account']==5080) & (Tacc2_adjusted['Year']==year),'Amount'].iloc[0]
      Interest_exp.append(interest_exp)
      depr_exp = Tacc2_adjusted.loc[(Tacc2_adjusted['Account']==5030) & (Tacc2_adjusted['Year']==year),'Amount'].iloc[0]
      Depreciation_exp.append(depr_exp)
      ebt = (gross_profit - total_op_exp) - interest_exp - depr_exp
      Income_Before_Tax.append(ebt)
      net_income = ebt
      Net_Income.append(net_income)

  Income_Statments = pd.DataFrame({
  'Year':Year,
  'Sales_Rev':Sales_Rev,
  'COGS':COGS,
  'Gross_Profit':Gross_Profit,
  'Rent_exp':Rent_exp,
  'Insurance_exp':Insurance_exp,
  'Salaries_exp':Salaries_exp,
  'Ad_exp':Ad_exp,
  'Total_Operating_exp':Total_Operating_exp,
  'EBITA':EBITA,
  'Interest_exp':Interest_exp,
  'Depreciation_exp':Depreciation_exp,
  'Income_Before_Tax':Income_Before_Tax,
  'Net_Income':Net_Income})



#------------------------- Balance Sheets --------------------------#

  Cash = []
  ARec = []
  Inventory = []
  Total_Current_Assets = []
  Land = []
  Equpiment = []
  Buildings = []
  Net_Accum_Depreciation = []
  Total_Assets = []
  Accounts_Payable = []
  Notes_Payable = []
  Total_Liability = []
  Retained_Earnings = []
  Total_Equity = []
  Total_Liabilities_Equity = []
  Year = []
  Balanced = []



  for year in Tacc2_adjusted['Year'].unique():
    if year <= End_Year:
      Year.append(year)
      cash = Tacc2_adjusted.loc[(Tacc2_adjusted['Account']==1000) & (Tacc2_adjusted['Year']==year),'Amount'].sum()
      Cash.append(cash)
      arec = Tacc2_adjusted.loc[(Tacc2_adjusted['Account']==1010) & (Tacc2_adjusted['Year']==year),'Amount'].sum()
      ARec.append(arec)
      inventory = Tacc2_adjusted.loc[(Tacc2_adjusted['Account']==1100) & (Tacc2_adjusted['Year']==year),'Amount'].sum()
      Inventory.append(inventory)
      tca = cash + arec + inventory
      Total_Current_Assets.append(tca)
      equipment = Tacc2_adjusted.loc[(Tacc2_adjusted['Account']==1230) & (Tacc2_adjusted['Year']==year),'Amount'].sum()
      Equpiment.append(equipment)
      equipment_depr = Tacc2_adjusted.loc[(Tacc2_adjusted['Account']==1231) & (Tacc2_adjusted['Year']==year),'Amount'].sum()
      Net_Accum_Depreciation.append(equipment_depr)
      total_asset = (cash + arec + inventory + equipment + equipment_depr).astype(float)
      Total_Assets.append(total_asset)
      ap = Tacc2_adjusted.loc[(Tacc2_adjusted['Account']==2000) & (Tacc2_adjusted['Year']==year),'Amount'].sum()
      Accounts_Payable.append(ap)
      notes = Tacc2_adjusted.loc[(Tacc2_adjusted['Account']==2020) & (Tacc2_adjusted['Year']==year),'Amount'].sum()
      Notes_Payable.append(notes)
      total_liability = ap + -notes
      Total_Liability.append(total_liability)
      retained_earnings = -Tacc2_adjusted.loc[(Tacc2_adjusted['Account']==3010) & (Tacc2_adjusted['Year']==year),'Amount'].sum() + Income_Statments.loc[(Income_Statments['Year']==year),'Net_Income'].sum()
      Retained_Earnings.append(retained_earnings*-1)

      total_equity = -retained_earnings
      Total_Equity.append(total_equity)
      total_liability_equity = (total_liability + total_equity)
      Total_Liabilities_Equity.append(total_liability_equity)

  Balance_Sheets_unadjusted = pd.DataFrame({
  'Year':Year,
  'Cash':Cash,
  'Arec':ARec,
  'Inventory':Inventory,
  'Total_Current_Assets':Total_Current_Assets,
  'Equipment':Equpiment,
  'Net_Accum_depr':Net_Accum_Depreciation,
  'Total_Assets':Total_Assets,
  'Accounts_Payable':Accounts_Payable,
  'Notes_Payable':Notes_Payable,
  'Total_Liability': Total_Liability,
  'Retained_Earnings':Retained_Earnings,
  'Total_Equity':Total_Equity,
  'Total_Liabilities_Equity':Total_Liabilities_Equity})

  Balance_Sheets = Balance_Sheets_unadjusted.cumsum().shift(1, fill_value=0) + Balance_Sheets_unadjusted
  Balance_Sheets['Year'] = Year

  Balance_Sheets['Balanced'] = (Balance_Sheets['Total_Assets'] + Balance_Sheets['Total_Liabilities_Equity']).abs() <= 2.00

  '''
  Print Financial Statments if needed

  with pd.ExcelWriter('combined_workbook.xlsx') as writer:
      Gen_Journal_df2.to_excel(writer, sheet_name='Gen_Journal', index=False)
      Income_Statments.to_excel(writer, sheet_name='Income_Statements', index=False)
      Balance_Sheets_unadjusted.to_excel(writer, sheet_name='Balance_Sheets_Unadjusted', index=False)
      Balance_Sheets.to_excel(writer, sheet_name='Balance_Sheets_Adjusted', index=False)
      Tacc2_adjusted.to_excel(writer, sheet_name='Tacc2_Adjusted', index=False)
  '''

  # Income Statment
  Income_Statments.to_sql('Income_Statments', conn, if_exists='replace', index=False)
  # Balance Sheets
  Balance_Sheets.to_sql('Balance_Sheets', conn, if_exists='replace', index=False)
  # General Ledger
  Gen_Journal_df2.to_sql('General_Journal', conn, if_exists='replace', index=False)
  # Sales Dataframe 
  sales_df.to_sql('Sub_Sales_Journal', conn, if_exists='replace', index=False)
  # Purchase Order Dataframe
  df_PO.to_sql('Sub_PO_Journal', conn, if_exists='replace', index=False)