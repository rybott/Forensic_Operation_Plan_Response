import pandas as pd
from typing import List, Dict, Json

''' Things to Do
1. Functions that Generate Ratios
2. Class that Generate Financial Statements From the Ratios
3. Class that calles the Generate Financial Statement and holds state of generated company through Json documents.
'''

class FSGenerator():
    def __init__(self, id: float, Ratios: Json, Assets: float = None, Sales: float = None) -> None:
        self.Ratios = Ratios[id]['ratios']
        self.Assets = Assets
        self.Sales = Sales
        self.RtoA = self.Ratios['Rev to Assets']
        if Assets:
            if Sales:
                print("Error - Missing Argument: function requires three arguments, Industry ID, Ratios, and either Asset or Sales")
            else:
                self.Sales = self.Assets * self.RtoA
        elif Sales:
            self.Assets= self.Sales / self.RtoA
        else:
            print("Error - Missing Arguemnt: function requires Industry ID, Ratios and starting figure Asset or Sales")

    def IS_Generator(self) -> Dict:
        self.Gprofit = self.Sales * self.Ratios['Gross Profit']
        self.COGS = self.Sales -  self.Gprofit
        self.Opexp = self.Sales * self.Ratios['Operating Expenses']
        self.Oprofit = self.Sales * self.Ratios['Operating Profit']
        self.OtherExp = self.Sales * self.Ratios['All Other Expenses (net)']

        self.Offset = self.Oprofit - self.OtherExp
        self.Check = self.Sales - self.COGS - self.Opexp - self.OtherExp

        # Adding Depreciation if there is excess exp Else it is Excess Exp
        depr = self.Sales * self.Ratios['% Depr, Depl, Amort / Sales - median']
        self.Depr = depr if depr < self.OtherExp - depr else self.OtherExp
        self.OtherExp = self.OtherExp - self.Depr

        # Adding Officers comp if there is excess exp Esle it is Excess Exp
        comp = self.Sales * self.Ratios["% Officers', Directors', Owners' Comp / Sales - median"]
        self.Comp = comp if comp < self.OtherExp - comp else self.OtherExp
        self.OtherExp = self.OtherExp - self.Depr

        self.NetIncome = self.sales - self.COGS - self.Opexp - self.OtherExp - self.Depr - self.Comp

        self.ISoutput = {
            'GProfit': self.Gprofit,
            'COGS': self.COGS,
            'Opexp': self.Opexp,
            'Oprofit':self.Oprofit,
            'OtherExp':self.OtherExp,
            'Depr': self.Depr,
            'Comp': self.Comp,
            'Offset':self.Offset}

        return self.ISoutput

    def Asset_Generator(self)-> Dict:
        self.ASoutput = {
            'Cash': self.Assets * self.Ratios['Cash & Equivalents'],
            'AR': self.Assets * self.Ratios['Trade Receivables - (net)'],
            'Inv': self.Assets * self.Ratios['Inventory'],
            'OtherCA': self.Assets * self.Ratios['All Other Current Assets'],
            'CA': self.Assets * self.Ratios['Total Current Assets'],
            'FA': self.Assets * self.Ratios['Fixed Assets (net)'],
            'Intan': self.Assets * self.Ratios['Intangibles (net)'],
            'OtherNCA': self.Assets * self.Ratios['All Other Non-Current Assets']}
        return self.ASoutput

    def Liability_Generator(self)-> Dict:
        self.LIoutput = {
            'Li': self.Assets * self.Ratios['Li'],
            'CNP': self.Assets * self.Ratios['CNP'],
            'CLTD': self.Assets * self.Ratios['CLTD'],
            'Ap': self.Assets * self.Ratios['Ap'],
            'TaxP': self.Assets * self.Ratios['TaxP'],
            'OtherCLi': self.Assets * self.Ratios['OtherCLi'],
            'CLi': self.Assets * self.Ratios['CLi'],
            'LTD': self.Assets * self.Ratios['LTD'],
            'DefTax': self.Assets * self.Ratios['DefTax'],
            'OtherNCLI': self.Assets * self.Ratios['OtherNCLI']}
        return self.LIoutput
