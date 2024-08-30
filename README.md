# Forensic Operations Plan and Response
### Purpose and Function
Names after the 1983 movie *WarGames*, the purpose of this project is to develop "War Games" 
for forensic and general accounting. As a forensic accountant, the main focus of the project is on 
forensics and audit, but it will also be a tool that one can use to learn how different accounting procedures
work outside of a classroom, but without the need for access to real books and records. I have tried to get as much help as 
I could from professionals in the field to insure the integrety of this tool for that purpose. This is a 
sandbox, that with a little tweeking, could model any company, fraud, or accounting procedure.

### Usage 
The User will have two options. The First is a tailored experience based on structured company scenarios that
will produce the same company and results based on the scenario. The Second, less structured mode, is Sandbox. 
This will have no presets, and everything will be editable, including adding your own financial data. This
will obviously be harder to do than the structured approach so it will take longer to be encorporated into the 
final product, but as I develop the scenarios, everything is a sandbox. 

## Further Considerations
### Fraud
- These will be locked to scenarios, as a senario will occur and within the base code, frauds will be implimented.
From there a master list of the frauds will be kept as well, allowing the users to find the fruad or in further
iterations, training a rule-based/machine-learning model to detect these frauds
- For Sales/Inventory
  - Excess Returns 
  - Missing Inventory (Inventory less than sales because of larceny)
  - Excessive Inventory (Inventory greater because of fictitious sales) For POs / Inventory
  - Missing Inventory (Inventory less than POs amount due to theft) Other Errors in Expected Margin calculations I have set the expected margin of excess inventory to 1.05x sales. So an ML model will be able to monitor quarterly levels and determine if that ratio is within an acceptable range
