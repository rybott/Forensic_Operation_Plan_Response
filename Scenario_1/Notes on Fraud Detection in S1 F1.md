# Notes on my ongoing research into fraud detection methods

## 11/22/2023 - KMean Clustering 
Status - Pending \ 
- I wanted to start with what I believe to be the most simple approach, and least likely to succeed
- Description: KMean Clustering is a ML clustering model that groups records into groups, hopefully fraud
and not fraud. I don't know if this will work for multiple reasons but mainly because it will look at each record
individually and not as a whole, something nessecary to determine fraud, but there is a chance.

- Methodology: I first generated 200 years of balance sheets (clean), and then 200 years of fraud at 10% (
1,000,000 sales, 10,000 fraudulent sales). I then concatenated the clean balance sheet and fraudulent balance sheet.
- Terms:
  - CP : Cash as Percent of Retained Earnings
  - ARP : Accounts Recievable (AR) as Percent of Retained Earnings
  - IP : Inventory (Inv) as Percent of Retained Earnings

- **Attempt 1**:
  - Status: Failure
  - Notes: Complete failure when analysing the entire balance sheet for 400 years (200 years with fraud, 200 without)
- **Attempt 2**:
  - Status: Failure
  - Notes: I wanted to see if the result changed when I targeted just the Cash, AR, Inv, and Retained Earnings Accounts
But this did not improve its abilties to seperate the two.
- **Attempt 3**:
  - Status: Tenative Sucsess
  - Notes: While the other two I was quite sure wouldn't work, I had high hopes for attempt 3, where I turned everything
into a percent of Retained Earnings (keeping the cut down dataframe from attempt 2). I was not disappointed with the results
getting just 6 out of the 400 misrepresented. But this is just the beginning, as further research needs to be done on this exact
dataset inorder to quantify the differences, and once I have determined that there is a significant relationship that the
model is determining through analysis and further study, then I can try lowering the fraud % as low as I can go to deremine
the feasability of this initial model, but current results are promising.
  - Further Analysis:
    - What is the average CP, ARP, and IP
    - What is the standard deviation of CIP, ARP, IP
    - How do those compare
    - What is Average Cash, AR, Inv accounts and what is the relationship to their CIP, ARP, IP
    - Compare these for each group to determine the change, Cash should be lower, AR and Inv higher, how is this reflected in the CIP, ARP, IP
  - Further Analysis conclusions
    |Group   |Value|Average (%)|Standard Deviation|
    |--------|-----|-----------|------------------|
    |1       |CP   |75.40      |.0398             |
    |2       |CP   |79.51      |.0415             |
    |Combined|CP   |77.84      |.0456             |
    |1       |ARP  |6.67       |.0417             |
    |2       |ARP  |1.60       |.0435             |
    |Combined|ARP  |4.15       |.0496             |
    |1       |IP   |17.53      |.0030             |
    |2       |IP   |18.39      |.0032             |
    |Combined|IP   |18.01      |.0057             |

    - First, the Standard deviation for each group is lower that combined, which does indicate a relationship between the data. While not definitive, this shows promising results towards using the Kmean model
    - The AR is much higher which I knew, but what is interesting is that the inventory was lower, again more research must be done but one would think it would be higher because fake sales means less inventory is being shipped out. Unless of course someone created a program that issued inventory based on sales and did not account for this in the fraudulent sales generator, in which case these findings make perfect sense, and this will be updated in further iterations.

