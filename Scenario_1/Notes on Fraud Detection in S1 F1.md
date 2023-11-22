# Notes on my ongoing research into fraud detection methods

## 11/22/2023 - KMean Clustering 
Status - Pending \ 
- I wanted to start with what I believe to be the most simple approach, and least likely to succeed
- Description: KMean Clustering is a ML clustering model that groups records into groups, hopefully fraud
and not fraud. I don't know if this will work for multiple reasons but mainly because it will look at each record
individually and not as a whole, something nessecary to determine fraud, but there is a chance.

- Methodology: I first generated 200 years of balance sheets (clean), and then 200 years of fraud at 10% (
1,000,000 sales, 10,000 fraudulent sales). I then concatenated the clean balance sheet and fraudulent balance
sheet.

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
