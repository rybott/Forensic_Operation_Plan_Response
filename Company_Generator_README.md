# Company Generation
## Purpose and Function
This Portion of the project contains the creation of a company. This company must be completely customizable, fluid and dynamic, and mimic to the best of my ability a real corporation:
1. Customizable
   - The User will be able to input data such as Years in Operation, Max/Min Quantity of Sales, and total number of sales
   - This will completely change the nature of the business. While this is just retail, using a min/max of 1/10 and total number of sales of 1 million compared to 1000/10000 and 1000 sales
  will change the feel of the business.
2. Fluid and Dynamic
   - This will be more than just simple Rev/Exp, Cr/Dr, I want to be able to apply nuance to the business through these scenarios, including but not limited to different investment strategies,
  and aquisitions, more complex topics to practice on as the program evolves.
3. Real Wold Properties
    - The Main purpose of this application is to create a sandbox for machine learning, and therefore this company needs to be accurate to the extent that I can learn how to develop mahcine leanring
   algorithms for the purpose of Audit and Forensics. 
  
### There are four main categories that need to be addressed in the creation of synthetic companies for the purpose of testing.
1. Sales, Revenue, Inventory
2. Other Operating Expenses
3. Other Compresensive Income
4. Reporting
5. Fraud

## Sales, Revenue, Inventory
Unlike in a real company, this is where the generator starts, because Revenue determines everything else about the buisness. 
- The Generator Creates Sales Data in the form of Orders, which have a price, data of order and shipment, and unit cost to aquire.
- From this data, the sale quanitites are agregated and purchase orders are created for the first of the month for each quarter in each year, corresponding the quantity of items sold in that quarter plus a buffer of .05% to mimic holding inventory
- Finanlly, both Sales and Purchases are aggreagted together into a single dataframe called inventory.
### Fraud
*For Sales*
- Missing Inventory (Inventory less than sales because of larceny)
- Excessive Inventory (Inventory greater becasue of fictious sales)
*For POs / Inventory*
- Missing Inventory (Inventory less than POs amount due to theft)
*Other*
- Errors in Expected Margin calculations
    - I have set the expected margin of excess inventory to 1.05x sales. So an ML model will be able to monitor quartely levels and determine if that ratio is within an acceptable range
### Further Considerations
- LIFO and FIFO Inventory by varying the Unit Cost
- Cost Accounting by varying Unit Price, determining what new price shoudl be based on market factors
Add things like market flucuation, maybe natural disasters, continuity
- Continuity: This is lacking in my current generator because each order is indidepent, which is realistic, as trends in the quantity and frequency of sales are present within product groups as well as YOY

## Expenses
- These are the other expenses such as rent and COGS which help the business function
- Some expenses will be have to have continuality, where one year impacts the value of the next and some epenses such as COGS have to be dependent on the sales quanitity as well.
### Steps
1. First Take your Total Revenue
2. Then you can decide what expenses you want to use, this will be decided by the scenario that the user chooses.
3. Each scenario will also include a profit margin, and you'll subtract Total Rev and Profit Margin to get Exp_Budget
4. Then you can take Exp_Budget and for each category Exp_Total_Year = Exp_Budget * % allcated
5. Finally, create all of the corresponding expenses for each year within their exp category.'
### Consideration for Exp
- *Fixed Expenses* - Rent, Pre-Paid Insurance, Depreciation, etc.
   - These will have to be calculated by taking the sum of the % allocations for all of the years, then dividing equally by 12 * number of years because these expenses generally don't change over time
- *COGS* - ( Begining Inventory ) * ( Unit_Cost + Purchases * Unit_Cost ) - ( Ending Inventory * Unit_Cost )
   - COGS has to be relevant to the sale and purchases of inventory
   - COGS will be calculated per Quarter for ease, Need to calculate the initial and ending inventory, and purchases is purchase orders for the quarter.
   - Unit Cost is already facotored in and therefore shouldn't matter but if needed this formula will give you unit_cost \
     Unit_Cost = (Begining Inventory + Purchases - Ending Inventory) / Rev * (COGS cost allocation)
  - New Idea I might have to do Rev - PM - COGS and then do the rest of the expenses
## Other Compresensive Income
## Reporting
## Fraud
