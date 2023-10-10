# Ep 1 Revenue through sales

Welcome back, today we will dive right in to the most important part of this project. 

To start once again my name is Ryan, I am getting my Masters in Accounting from Baruch and I have no life leading me to creating this sythetic company generator, and today we give the company life.

- Revenue can take many forms, especially when trying to generate a company that can imitate literally anything, but the general concept is the same, money for goods or services, and it is also the driving force in any company, no revenue no more buisness. 

- That is why we will working backwards, generating a list of revenue generating transactions and then developing the company around that. 

- To start, we have to talk about what we want to have a revenue generating transaction look like. The Interesting thing is that this transaction does not need to be defined because the we haven't defined what the company actually does to generate revenue at this point. 
What we actually need is just these items. Note that the:
    - Shipment_date: can be same as order date for services
    - StoreID/Name: can be null
    - Product_Type: can be a service if nesessary
    - Unit_Price: PRice of service
    - Unit_Cost: this is COGS and for now it is known but we can also make it calculated later on for manufactorures but I want to keep this simple
    - Quantity can be one for services
    - The other columns are just quick calculations useful later on.

- As you can see the Revenue is very versitile and will be able to be used for vertually every scenario. It can also be replaced all together, if real financial data is provided, as long as we have the right fields in the real data we can plug it in and do all of the same calculations without a single issue. 

- That is all for this video, we have the most important... and easiest portion of the code base but we are well on our way. 

- Note also all of the code that I have is in the Jupitor Notebook test_notebook_v2 for now, but in a seperate video I'll go over refactoring the code into seperated PY files, and depending on when you watch this video it might already be included in my github. 
    