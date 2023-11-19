# Fraud 1
# Import
import pandas as pd
import numpy as np
from datetime import timedelta
import duckdb as ddb


def Generate_Fraud1(conn,Clean_General_Journal,regions_df,products_df,start_date,end_date,num_records):
    Start_Year = start_date.strftime('%Y')
    End_Year = int(end_date.strftime('%Y'))

    # ----------------------- Generate the Fraudulent Sales -------------------#
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
        shipment_dates.append(random_date + timedelta(days=np.random.randint(1, 7)))

        # Random quantity between 1000 and 10000
        quantities.append(np.random.randint(1000, 10001))

    # Initial Inventory Levels
    Inventory_dict = {'Cereal':0, 'Snacks':0, 'Beverages':0, 'Baby Food':0, 'Meat':0, 'Fruits':0, 'Vegetables':0, 'Personal Care':0, 'Cosmetics':0, 'Household':0, 'Office Supplies':0, 'Clothes':0}
    Vendor_dict = {'Cereal':'Foodco', 'Snacks':'Foodco', 'Beverages':'Foodco', 'Baby Food':'Foodco', 'Meat':'Farmco', 'Fruits':'Farmco', 'Vegetables':'Farmco', 'Personal Care':'Beautyco', 'Cosmetics':'Beautyco', 'Household':'Homeco', 'Office Supplies':'Homeco', 'Clothes':'Fashionco'}

    Fraudulent_sales_df = pd.DataFrame({
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

    Fraudulent_sales_df['Total Profit'] = Fraudulent_sales_df['Revenue'] - Fraudulent_sales_df['Total_Cost']


    #-------------------Total Revenue Calculations For Analysis---------------#

    # Total Revenue
    qry_Trev = '''
        SELECT YEAR(Shipment_Date) AS Year, SUM(Revenue) AS Revenue
        FROM Fraudulent_sales_df
        GROUP BY Year
        Order By Year
    '''

    # Total Revenue Per Product Per year
    qry_rev = '''
        SELECT YEAR(Shipment_Date) AS Year, Product_Type AS Product, SUM(Revenue) AS Revenue, Unit_Cost
        FROM Fraudulent_sales_df
        GROUP BY Year, Product, Unit_Cost
        Order By Year
    '''

    df_Trev = ddb.sql(qry_Trev).df()
    df_rev = ddb.sql(qry_rev).df()

    Rev_FromFraud_dict = dict(zip(df_Trev['Year'],df_Trev['Revenue']))

    #------------------------------Journals-------------------------#
    Account = []
    Date = []
    Description = []
    Amount = []
    Dr_Cr = []

    Fraud_Journal_df = pd.DataFrame({
        'Account':Account,
        'Date':Date,
        'Description': Description,
        'Amount':Amount,
        'Dr_Cr':Dr_Cr})

    #---------------------------Sales Journals----------------------#

    # Add the index as a column in the dataframe
    Fraudulent_sales_df = Fraudulent_sales_df.reset_index()


    Fraudulent_sales_df['AccountDr'] = 1010
    Fraudulent_sales_df['Debit'] = "Debit"
    Fraudulent_sales_df['AccountCr'] = 4000
    Fraudulent_sales_df['Credit'] = "Credit"
    Fraudulent_sales_df['desc'] = Fraudulent_sales_df['index'].astype(str) + "_Sale of Inventory"

    FSales_dr = Fraudulent_sales_df[['AccountDr','Order_Date','desc','Revenue','Debit']]
    FSales_cr = Fraudulent_sales_df[['AccountCr','Order_Date','desc','Revenue','Credit']]
    FSales_dr.columns = Fraud_Journal_df.columns
    FSales_cr.columns = Fraud_Journal_df.columns

    Fraud_Journal_df = pd.concat([FSales_dr,FSales_cr,Fraud_Journal_df], ignore_index=True)

    # Concat the Fraud Journal and the General Journal


    Master_Journal_df = pd.concat([Fraud_Journal_df,Clean_General_Journal], ignore_index=True)
    Master_Journal_df['Date'] = pd.to_datetime(Master_Journal_df['Date'])
    Master_Journal_df['Date'] = Master_Journal_df['Date'].dt.strftime('%Y-%m-%d %H:%M:%S')


    #--------- Perform all of the same steps to get the new adjusted financial statments ----------------#
    # Step 1
    qry_Tacc1 = '''
    SELECT
        Account,
        CAST(Date AS DATE) as Date,
        CASE
            WHEN Dr_Cr = 'Credit'
            THEN Amount * -1
            WHEN Dr_Cr = 'Debit'
            THEN Amount
        END AS Amount
    FROM Master_Journal_df
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
    Tacc2_adjusted = Tacc2[Tacc2['Year'] <= End_Year].copy()

    

    #-------------------------Fraud Income Statments-----------------------#

    Year = []
    Sales_Rev = []
    Gross_Profit = []
    EBITA = []
    Income_Before_Tax = []
    Net_Income = []

    # Making all the non_affected accounts zero
    COGS = [0] * len(Tacc2_adjusted['Year'].unique())
    Rent_exp = [0] * len(Tacc2_adjusted['Year'].unique())
    Insurance_exp = [0] * len(Tacc2_adjusted['Year'].unique())
    Salaries_exp = [0] * len(Tacc2_adjusted['Year'].unique())
    Ad_exp = [0] * len(Tacc2_adjusted['Year'].unique())
    Total_Operating_exp = [0] * len(Tacc2_adjusted['Year'].unique())
    Interest_exp = [0] * len(Tacc2_adjusted['Year'].unique())
    Depreciation_exp = [0] * len(Tacc2_adjusted['Year'].unique())
    Income_Tax = [0] * len(Tacc2_adjusted['Year'].unique())

    for year in Tacc2_adjusted['Year'].unique():
        if year <= End_Year:
            Year.append(year)
            sales_rev = Tacc2_adjusted.loc[(Tacc2_adjusted['Account']==4000) & (Tacc2_adjusted['Year']==year),'Amount'].iloc[0] * -1
            Sales_Rev.append(sales_rev)
            Gross_Profit.append(sales_rev)
            EBITA.append(sales_rev)
            Income_Before_Tax.append(sales_rev)
            Net_Income.append(sales_rev)

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
    # Print Financial Statments - Turn into Save Financial Statments into the Company Database
    with pd.ExcelWriter('combined_Fraud_workbook.xlsx') as writer:
        Master_Journal_df.to_excel(writer, sheet_name='Master_Gen_Journal', index=False)
        Income_Statments.to_excel(writer, sheet_name='F_Income_Statements', index=False)
        Balance_Sheets_unadjusted.to_excel(writer, sheet_name='F_Balance_Sheets_Unadjusted', index=False)
        Balance_Sheets.to_excel(writer, sheet_name='F_Balance_Sheets_Adjusted', index=False)
        Tacc2_adjusted.to_excel(writer, sheet_name='Tacc2_Adjusted', index=False)
    '''
    
    # Income Statment
    Income_Statments.to_sql('F_Income_Statments', conn, if_exists='replace', index=False)
    # Balance Sheets
    Balance_Sheets.to_sql('F_Balance_Sheets', conn, if_exists='replace', index=False)
    # General Ledger
    Master_Journal_df.to_sql('Master_Journal', conn, if_exists='replace', index=False)
    # Sales Dataframe 
    Fraud_Journal_df.to_sql('F_Fraud_Ledger', conn, if_exists='replace', index=False)
    # Purchase Order Dataframe
    Fraudulent_sales_df.to_sql('Fraudulent_Sales', conn, if_exists='replace', index=False)
