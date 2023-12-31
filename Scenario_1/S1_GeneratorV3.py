import pandas as pd
import numpy as np
from datetime import timedelta
import random
import duckdb as ddb
import sqlite3 as sql

# Further Analysis
import matplotlib.pyplot as plt
import plotly.express as px


def Generate_Scenario_12(conn, 
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
                        Preprogram_Useful_Life,
                        Note_Payment_Yrs,
                        Note_Interest_Yrly,
                        Note_Payment_Remaining,
                        Initial_Cash):
    
    Start_Year = start_date.strftime('%Y')
    End_Year = int(end_date.strftime('%Y'))
    
    products = products_df.sample(n=num_records, replace=True).reset_index(drop=True)
    stores = stores_df.sample(n=num_records, replace=True).reset_index(drop=True)

    quantities = np.random.randint(items_per_order[0], items_per_order[1], num_records)

    days_diff = (end_date - start_date).days
    random_days = np.random.randint(0, days_diff, num_records)
    order_dates = start_date + pd.to_timedelta(random_days, unit='d')
    shipment_days = np.random.randint(1, 51, num_records)
    shipment_dates = order_dates + pd.to_timedelta(shipment_days, unit='d')

    revenue = products['Unit_Price'].values * quantities
    total_cost = products['Unit_Cost'].values * quantities


    sales_df = pd.DataFrame({
    'Order_Date': order_dates,
    'Shipment_Date': shipment_dates,
    'StoreID': stores['StoreID'],
    'StoreName': stores['StoreName'],
    'Product_Type': products['Product'],
    'Unit_Price': products['Unit_Price'],
    'Unit_Cost': products['Unit_Cost'],
    'Quantity': quantities,
    'Revenue': revenue,
    'Total_Cost': total_cost,
    'Total Profit': revenue - total_cost,
    'Vendor': products['Vendor']
    })

    Inventory_dict = products_df.set_index('Product')['Initial_Inventory'].to_dict()
    Initial_Inventory_dict = Inventory_dict.copy()

    sales_df2 = sales_df.sort_values(by='Shipment_Date')
    sales_df2['Shipment_Quarter'] = sales_df2['Shipment_Date'].dt.to_period('Q')

    grouped_sales_df = sales_df2.groupby(['Product_Type', 'Shipment_Quarter']).agg({
    'Quantity': 'sum',
    'Vendor': 'first',
    'Unit_Cost': 'first',
    'Total_Cost': 'sum'
    }).reset_index()   

    PO_df = pd.DataFrame(columns=['OrderID', 'Product', 'Vendor', 'Unit_Cost', 'Quantity', 'Shipment_Quarter', 'InventoryBeg', 'InventoryEnd'])

    for product in grouped_sales_df['Product_Type'].unique():
        product_sales = grouped_sales_df[grouped_sales_df['Product_Type'] == product]
        beg_inventory = Inventory_dict[product]
        inventory = Inventory_dict[product]
        purchase_orders = []
  
        for index, row in product_sales.iterrows():
            quantity_sold = row['Quantity']
            order_date = row['Shipment_Quarter']

            inventory -= quantity_sold
            if inventory < 0:
                purchase_quantity = abs(inventory) * 1.05  # Additional 5% for having more inventory than sales
                inventory += purchase_quantity
                end_inventory = inventory
                purchase_orders.append({
                    'OrderID': index,
                    'Product': product,
                    'Vendor': row['Vendor'],
                    'Unit_Cost': row['Unit_Cost'],
                    'Quantity': purchase_quantity,
                    'Shipment_Quarter': order_date,
                    'InventoryBeg': beg_inventory,
                    'InventoryEnd': end_inventory 
                })

            # Update Inventory_dict for next iteration
            Inventory_dict[product] = inventory

        PO_df = pd.concat([PO_df, pd.DataFrame(purchase_orders)], ignore_index=True)

    quarter_to_month = {'1': '01', '2': '04', '3': '07', '4': '10'}

    PO_df['Year'] = PO_df['Shipment_Quarter'].dt.year
    PO_df['Year'] = PO_df['Year'].astype(str)
    PO_df['Quarter'] = PO_df['Shipment_Quarter'].dt.quarter.astype(str)
    PO_df['Day'] = PO_df['Quarter'].map(quarter_to_month)
    PO_df['Purchase_Date'] = pd.to_datetime(PO_df['Year'] + '-' + PO_df['Day'], errors='coerce')

    df_PO = PO_df.drop(['Year','Quarter','Day','Shipment_Quarter'], axis=1)

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
    df_PO['COGS_Quantity'] =  df_PO['InventoryBeg'] +df_PO['Quantity'] - df_PO['InventoryEnd']

    COGS_df1 = df_PO[['Purchase_Date','Product','COGS_Quantity','Unit_Cost']]

    COGS_qry1 = '''
        SELECT
            CAST(
            CASE
                WHEN Quarter(Purchase_Date) = 1
                THEN CONCAT(YEAR(Purchase_Date), '-01-30')
                WHEN Quarter(Purchase_Date) = 2
                THEN CONCAT(YEAR(Purchase_Date), '-04-30')
                WHEN Quarter(Purchase_Date) = 3
                THEN CONCAT(YEAR(Purchase_Date), '-07-30')
                WHEN Quarter(Purchase_Date) = 4
                THEN CONCAT(YEAR(Purchase_Date), '-10-30')
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

    Gen_Journal_df = pd.DataFrame(columns=[
        'Account',
        'Date',
        'Description',
        'Amount',
        'Dr_Cr'])

    #---------------------------Sales Journals----------------------#

    sales_df2 = sales_df2.reset_index()

    sales_df2['AccountDr'] = np.random.choice([1010, 1000], size=len(sales_df2), p=[0.7, 0.3])
    sales_df2['Debit'] = "Debit"
    sales_df2['AccountCr'] = 4000
    sales_df2['Credit'] = "Credit"
    sales_df2['desc'] = sales_df2['index'].astype(str) + "_Sale of Inventory"

    debit_acc = sales_df2[['AccountDr','Order_Date','desc','Revenue','Debit']]
    credit_acc = sales_df2[['AccountCr','Order_Date','desc','Revenue','Credit']]
    debit_acc.columns = Gen_Journal_df.columns
    credit_acc.columns = Gen_Journal_df.columns

    Gen_Journal_df = pd.concat([debit_acc,credit_acc,Gen_Journal_df], ignore_index=True)
   

    #-------------------------------Purchase Order Journal----------------#
    df_PO = df_PO.reset_index()

    df_PO['AccountDr'] = 1100
    df_PO['Debit'] = "Debit"
    df_PO['AccountCr'] = 2000
    df_PO['Credit'] = "Credit"
    df_PO['Amount'] = df_PO['Unit_Cost']*df_PO['Quantity']
    df_PO['desc'] = df_PO['index'].astype(str) + "_Purchase of Inventory"

    debit_acc = df_PO[['AccountDr','Purchase_Date','desc','Amount','Debit']]
    credit_acc = df_PO[['AccountCr','Purchase_Date','desc','Amount','Credit']]
    debit_acc.columns = Gen_Journal_df.columns
    credit_acc.columns = Gen_Journal_df.columns

    Gen_Journal_df = pd.concat([debit_acc,credit_acc,Gen_Journal_df], ignore_index=True)


    #-------------------------COGS Journal---------------------------#

    COGS_df = COGS_df.reset_index()

    COGS_df['AccountDr'] = 5000
    COGS_df['Debit'] = "Debit"
    COGS_df['AccountCr'] = 1100
    COGS_df['Credit'] = "Credit"
    COGS_df['desc'] = df_PO['index'].astype(str) + "_Quarterly COGS"

    debit_acc = COGS_df[['AccountDr','Date','desc','Value','Debit']]
    credit_acc = COGS_df[['AccountCr','Date','desc','Value','Credit']]
    debit_acc.columns = Gen_Journal_df.columns
    credit_acc.columns = Gen_Journal_df.columns

    Gen_Journal_df = pd.concat([debit_acc,credit_acc,Gen_Journal_df], ignore_index=True)


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


    # Paying off AP 
    AP_Gen_Journal_df = Gen_Journal_df[Gen_Journal_df['Account'] == 2000].copy()

    AP_Gen_Journal_df = AP_Gen_Journal_df.reset_index()

    AP_Gen_Journal_df['AccountDr'] = 2000
    AP_Gen_Journal_df['Debit'] = "Debit"
    AP_Gen_Journal_df['AccountCr'] = 1000
    AP_Gen_Journal_df['Credit'] = "Credit" 
    AP_Gen_Journal_df['DatePaid'] = AP_Gen_Journal_df['Date'] + timedelta(days=30)
    AP_Gen_Journal_df['desc'] = AP_Gen_Journal_df['index'].astype(str) + "_Paided down AP liability"

    debit_acc = AP_Gen_Journal_df[['AccountDr','DatePaid','desc','Amount','Debit']]
    credit_acc = AP_Gen_Journal_df[['AccountCr','DatePaid','desc','Amount','Credit']]
    debit_acc.columns = Gen_Journal_df.columns
    credit_acc.columns = Gen_Journal_df.columns

    Gen_Journal_df = pd.concat([debit_acc,credit_acc,Gen_Journal_df], ignore_index=True)


    # Paying off Recievables
    AR_Gen_Journal_df = Gen_Journal_df[Gen_Journal_df['Account'] == 1010].copy()

    AR_Gen_Journal_df['AccountDr'] = 1000
    AR_Gen_Journal_df['Debit'] = "Debit"
    AR_Gen_Journal_df['AccountCr'] = 1010
    AR_Gen_Journal_df['Credit'] = "Credit"
    AR_Gen_Journal_df['Paid_Time_Difference'] = np.random.randint(5, 101, size=len(AR_Gen_Journal_df))
    AR_Gen_Journal_df['DateRecieved'] = AR_Gen_Journal_df['Date'] + pd.to_timedelta(AR_Gen_Journal_df['Paid_Time_Difference'], unit='d')
    AR_Gen_Journal_df['desc'] = "Recieved Recievables after" + AR_Gen_Journal_df['Paid_Time_Difference'].astype(str) + "late"

    debit_acc = AR_Gen_Journal_df[['AccountDr','DateRecieved','desc','Amount','Debit']]
    credit_acc = AR_Gen_Journal_df[['AccountCr','DateRecieved','desc','Amount','Credit']]
    debit_acc.columns = Gen_Journal_df.columns
    credit_acc.columns = Gen_Journal_df.columns

    Gen_Journal_df = pd.concat([debit_acc,credit_acc,Gen_Journal_df], ignore_index=True)


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

    Tacc2_filtered = Tacc2[Tacc2['Year'] <= End_Year].copy()
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
    
    return Gen_Journal_df2