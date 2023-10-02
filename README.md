# Company Generation 
The first phase of this two-phase project
## Purpose and Function
This Portion of the project contains the creation of a company. This company must be completely customizable, fluid, and dynamic, and mimic to the best of my ability a real corporation:
1. Customizable
   - The User will be able to input data such as Years in Operation, Max/Min Quantity of Sales, and total number of sales
   - This will completely change the nature of the business. While this is just retail, using a min/max of 1/10 and a total number of sales of 1 million compared to 1000/10000 and 1000 sales
  will change the feel of the business.
2. Fluid and Dynamic
   - This will be more than just simple Rev/Exp, Cr/Dr, I want to be able to apply nuance to the business through these scenarios, including but not limited to different investment strategies,
  and acquisitions, more complex topics to practice as the program evolves.
3. Real World Properties
    - The main purpose of this application is to create a sandbox for machine learning, and therefore this company needs to be accurate to the extent that I can learn how to develop machine learning
   algorithms for Audit and Forensics. 

## Further development
This Generator generates 100% of the data, but at every possible point there is the ability for the user to, using their own company's data, generate financial data similar to their own. For now, the only revenue source is marketing, but in the future, more can be created, but any number of expenses, volume of sales, or any other characteristic of a business can be programmed into the system. In the future, if this was a business idea, a form could be filled out with the company's information, and then that form could feed into the program and tweak the necessary parameters to match the company for models, analysis, and predictions. 

### four main categories need to be addressed in the creation of synthetic companies for testing.
1. Sales, Revenue, Inventory
2. Other Operating Expenses
3. Other Comprehensive Income
4. Reporting
5. Fraud

## Sales, Revenue, Inventory
Unlike in a real company, this is where the generator starts, because Revenue determines everything else about the business. 
- The Generator Creates Sales Data in the form of Orders, which have a price, date of order and shipment, and unit cost to acquire.
- From this data, the sale quantities are aggregated and purchase orders are created for the first of the month for each quarter in each year, corresponding to the quantity of items sold in that quarter plus a buffer of .05% to mimic holding inventory
- Finally, both Sales and Purchases are aggregated together into a single data frame called inventory.
### Fraud
*For Sales*
- Missing Inventory (Inventory less than sales because of larceny)
- Excessive Inventory (Inventory greater because of fictitious sales)
*For POs / Inventory*
- Missing Inventory (Inventory less than POs amount due to theft)
*Other*
- Errors in Expected Margin calculations
    - I have set the expected margin of excess inventory to 1.05x sales. So an ML model will be able to monitor quarterly levels and determine if that ratio is within an acceptable range
### Further Considerations
- LIFO and FIFO Inventory by varying the Unit Cost
- Cost Accounting by varying Unit Price, determining what new price should be based on market factors
Add things like market fluctuation, maybe natural disasters, continuity
- Continuity: This is lacking in my current generator because each order is independent, which is realistic, as trends in the quantity and frequency of sales are present within product groups as well as YOY

## Expenses
- Some expenses will have to have continuity, where one year impacts the value of the next and some expenses such as COGS have to be dependent on the sales quantity as well.
- Expenses are processed in two stages just as on an income statement, first COGS is calculated and removed for Gross Profit, based on ChatGPT, expenses are calculated yearly as a percent of gross profit with the percentage falling in between a range so it is still random (except fixed costs such as Income Tax which is a single percentage.) 

### Common Expense Categories as Percentage of Gross Profit
**Operating Expenses (OPEX)**
- Sales & Marketing (S&M): 5% - 20%
- Research & Development (R&D): 5% - 15%
  - Note: Higher for tech and pharmaceutical companies.
- General & Administrative (G&A): 6% - 18%
- Rent or Lease: 2% - 10%
  - Note: Lower for digital businesses, higher for brick-and-mortar.

**Interest Expense**
- Range: 0.5% - 5%
  - Note: Varies with the company's debt level.

**Depreciation & Amortization**
- Range: 2% - 10%
  - Note: Higher for businesses reliant on tangible assets.

**Other Expenses**
- Range: 1% - 5%

**Taxes**
- *Not a Range*


### Steps
1. First Take your Total Revenue
2. Then you can subtract COGS aggregated yearly
4. After, using predetermined ranges, a random % of the gross profit is assigned for each expense
5. Finally, a data frame with all the yearly expense category totals can be used to create expenses
### Consideration for Exp
- *Fixed Expenses* - Rent, Pre-Paid Insurance, Depreciation, etc.
   - These will have to be calculated by taking the sum of the % allocations for all the years, then dividing equally by 12 * the number of years because these expenses generally don't change over time
- *COGS* - ( Begining Inventory ) * ( Unit_Cost + Purchases * Unit_Cost ) - ( Ending Inventory * Unit_Cost )
   - COGS has to be relevant to the sale and purchases of inventory
   - COGS will be calculated per Quarter for ease, Need to calculate the initial and ending inventory, and purchases are purchase orders for the quarter.
   - Unit Cost is already factored in and therefore shouldn't matter but if needed this formula will give you unit_cost \
     Unit_Cost = (Begining Inventory + Purchases - Ending Inventory) / Rev * (COGS cost allocation)
  - New Idea I might have to do Rev - PM - COGS and then do the rest of the expenses
## Other Comprehensive Income
## Reporting
## Fraud
