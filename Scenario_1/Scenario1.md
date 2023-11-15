# Scenario One
This is the most basic Scenario for a simple business. A Boutique Merchant that purchases products and then resells them for profit. The business has a storefront.
The COGS includes both the purchase and shipment of products and does not need to be calculated like a manufacturing business.
In this scenario, the company already owns Land and Equipment (Tills, forklifts, etc.). 

## Expenses
### Fixed
Fixed expenses do not change over the years, so instead a variable revenue is calculated for every year, and a variable percent of revenue is 
calculated every year (just like a variable cost) but then those calculated costs per year are added up and divided by the number of months in all 
the years, thus turning a variable cost into a fixed cost. 

- Rent (6% - 10% of Revenue)
- Insurance (2% - 4% of Revenue)
- Wages (15% - 20% of Revenue)

### Variable
- Advertising (6% - 8% of Revenue)
  - is the only variable expense, and is calculated on random days as a percent of the rev

## Other Assets
- Equipment
  - Equipment is increased (Asset) and Notes Payable is also increased (Liability)
  - There are Notes payments and Interest Payments from Cash
    - Cash will be *Rev - Exp* but it is important to make sure there is enough cash to cover these payments,
      so at the end of each year, a calculation will see if there is enough cash and then systematically add the
      correct value of Cash on hand to the first year, making sure everything is balanced.
      - Cash is increased (Asset) and Retained Earnings is also increased (Equity)

     
## Financial Statments
- Balance Sheet
  - By the end this should be balanced for each of the years

|Code|**Balance Sheet**|Account|Amount|
|---|---|---|---|
|1000|Cash||xxx|
|1010|Accounts Recievable||xxx|
|1100|Inventory||xxx|
|0001||Total Current Assets|xxx|
|1250|Land||xxx|
|1230|Equipment||xxx|
|1231|Accumulated Depreciation||(xxx)|
|0002||Total Asset|xxx|
|2000|Accounts Payable||xxx|
|2020|Notes Payable||xxx|
|0004||Total Liability|xxx|
|3010|Retained Earnings||xxx|
|0005||Total Equity|xxx|
|0006|***Total Liabilities and Equity***||xxx|

|Code|**Income Statment**||Amount|
|---|---|---|---|
|4000|Sales Rev||xxx|
|5000|COGS||(xxx)|
|0007|Gross Profit||xxx|
|5110|Rent Exp||xxx|
|5050|Insurance Exp||xxx|
|5010|Salaries Exp||xxx|
|0008||Total Operating Exp|xxx|
|0009||Operating Income|xxx|
|0010||EBITA|xxx|
|6000|Interest Income||(xxx)|
|0013||Income Before Tax|xxx|
|0014|Income Tax|||
|0015|***Net Income***||xxx|

### I am having trouble getting the cash flow to generate and put a pin in it until Cash Flow statment is nessecary
|Code|**Cash Flow**|||
|---|---|---|---|
|0000|I. Operating Activities|||
|0015|Net Income||xxx|
|5030|Depreciation||xxx|
|1010|(+)/- Accounts Recivable||xxx|
|2000|+/(-) Accounts Payable||xxx|
|1100|(+)/- Inventory||xxx|
|0012|+/(-) Interest Income||xxx|
|0016||Net Cash From Operations|xxx|
|0000|II. Investing Activities|||
|0000|None For this Scenario|||
|0000|III. Financing Activities|||
|2020|(-)/+ Notes Payable||(xxx)|
|0018||Net Cash From Financing|xxx|
|0019|Begining Cash Balance||xxx|
|0020|End Cash Balance||xxx|
|0021|***Net Cash Flow***||xxx|


# Fraud 
## Fraud One - Inventory
- Fraud Ledger: An accompanying general ledger that will contain all of the fraudulent transactions added to the financial statments
- Target Ledger: This will have a mix of the General and Fraud Ledgers, and create the Target Financial Statments too, regenerating the company with fraud
**S1F1**: Inventory not decreasing at the same rate as Sales. 
  - The First fraud for Scenario 1, this will contain **Fake Sales**
  - First update the fraud ledger like you would a regular sale
  - Journal Entries
    | Account Title      | Dr  | Cr  |
    | ------------------ | --- | --- |
    | AR (Can't be Cash) | xxx |     |
    | Sales              |     | xxx |
  - Effects on Target Financial Statements
    - Increase Assets + Increased Retained Earnings (Income Statments) = Balanced
  - Can be detected two ways:
    - Detecting higher than expected inventory numbers
    - Detecting abnormally higher AR /  high AR Aging / low AR Turnover
      - AR aging and Turnover will need the construction of a recievables schedule
  - In the future I can also use store location of fraud to detect which store is having the issue. All found in the Fraud Ledger
  
**S1F2**: Sales Rising without a coresponding increase in COGS or Inventory deplecition
