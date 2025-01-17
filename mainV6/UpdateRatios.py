import json
import os
import pandas as pd


directory = r"C:\Users\rybot\OneDrive\Desktop\rma"
ratio_json = r"C:\Design Folder\RBGithub\Forensic_Operation_Plan_Response\Ratios.json"

with open("Ratios.json", "r") as reader:
    imported_json = json.load(reader)

for file_name in os.listdir(directory):
    if file_name.endswith('.xls') or file_name.endswith('.xlsx'):
        id = file_name[:file_name.find(" ")]

        if id in imported_json.keys():
            print(f"{id} already in database")
        else:
            print(id)
            id = id[:id.find(".x")]
            file_path = os.path.join(directory, file_name)
            df = pd.read_excel(file_path, sheet_name='FRB Sales', skiprows=4)

            first_col = df.columns[0]
            values = df[[first_col,'All']]

            imported_json[id] = {"description": "", "ratios": {"Cash & Equivalents": None ,"Trade Receivables - (net)": None ,"Inventory": None ,"All Other Current Assets": None ,"Total Current Assets": None ,"Fixed Assets (net)": None ,"Intangibles (net)": None ,"All Other Non-Current Assets": None ,"Total Assets": None ,"Notes Payable-Short Term": None ,"Cur. Mat.-L/T/D": None ,"Trade Payables": None ,"Income Taxes Payable": None ,"All Other Current Liabilities": None ,"Total Current Liabilities": None ,"Long Term Debt": None ,"Deferred Taxes": None ,"All Other Non-Current Liabilities": None ,"Net Worth": None ,"Total Liabilities & Net Worth": None ,"Net Sales": None ,"Gross Profit": None ,"Operating Expenses": None ,"Operating Profit": None ,"All Other Expenses (net)": None ,"Profit Before Taxes": None ,"EBITDA": None ,"EBIT / Interest - median": None ,"Net Profit + DDA / Curr Mat LTD - median": None ,"% Depr, Depl, Amort / Sales - median": None ,"% Officers', Directors', Owners' Comp / Sales - median": None ,"Rev to Assets": None ,"Interest":None}}

            ratios = imported_json[id]['ratios'].keys()
            for ratio in ratios:
                try:
                    value = df.loc[df[first_col] == ratio, 'All'].values[0]
                    if "[" in value:
                        value = value[value.find("]")+1:].strip()
                    elif ")" in value:
                        value = value[value.find(")")+1:].strip()
                    value = float(value)
                    imported_json[id]['ratios'][ratio] = value
                except:
                    pass
                if ratio == "Rev to Assets":
                    try:
                        Sales_AR = "Sales / Receivables - median"
                        AR_Assets = "Trade Receivables - (net)"
                        Sales_AR = df.loc[df[first_col] == Sales_AR, 'All'].values[0]
                        AR_Assets = df.loc[df[first_col] == AR_Assets, 'All'].values[0]

                        imported_json[id]['ratios'][ratio] = Sales_AR * AR_Assets
                    except:
                       pass

                if ratio == "Interest":
                    try:
                        ebit_curltd = "Net Profit + DDA / Curr Mat LTD - median"
                        ebit_interst = "EBIT / Interest - median"
                        curltd_sales = "Trade Receivables - (net)"

                        Interest = (ebit_curltd / ebit_interst)/(1/curltd_sales)
                        imported_json[id]['ratios'][ratio] = Interest
                    except:
                        pass

            # Check Data Integrity
            missing_values = []
            for ratio in ratios:
                value = imported_json[id]['ratios'][ratio]
                if value == None:
                    missing_values.append(ratio)
            if len(missing_values) > 0:
                print("For Following Ratios are Missing Values:")
                for val in missing_values:
                    print(f"-{val}")
                user = input("Are you sure you want to add this industry to the database? Y/N  ")
                if user.upper() == "Y" or user.upper() == "Yes":
                    with open("Ratios.json", "w") as writer:
                        json.dump(imported_json, writer)
            else:
                with open("Ratios.json", "w") as writer:
                    json.dump(imported_json, writer)
