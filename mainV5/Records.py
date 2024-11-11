import random
import pandas as pd

class RecordingFunctions: 
    def __init__(self, Data_Manager):
        self.Data = Data_Manager

    # Bulk Data Processing
    def JournalEntries_Bulk(self, Clean_df, DebitAcc, CreditAcc, probability=None, val1=0, val2=0, p1=0, p2=0):
        if probability == None:
            pass
        elif probability.lower() == 'dr':
            DebitAcc = random.choices

        df_debits = Clean_df[['Date','Amount']].copy()
        df_debits['Account'] = DebitAcc
        df_debits['Balance'] = "Debit"
        self.Data.ConcatData('journal',df_debits)

        df_credits = Clean_df[['Date','Amount']].copy()
        df_credits['Account'] = CreditAcc
        df_credits['Balance'] = "Credit"
        self.Data.ConcatData('journal',df_credits)

    # Row by Row Data Processing
    def JournalEntries_Single(self, Date, Amount, DebitAcc, CreditAcc):
        self.General_Journal = pd.DataFrame({"Date":[],"Amount":[],"Account":[],"Balance":[]})
        if isinstance(Amount, list) and isinstance(DebitAcc, list) and isinstance(CreditAcc, list):
            if len(Amount) == len(DebitAcc) + len(CreditAcc):
                len_ofDr = len(DebitAcc)
                DrAmounts = Amount[:len_ofDr]
                CrAmounts = Amount[len_ofDr:]
                Debits = zip(DebitAcc,DrAmounts)
                Credits = zip(CreditAcc,CrAmounts)
                for dr, amount in Debits:
                    Journal_Entry = [Date, dr, amount, "Debit"]
                    self.General_Journal.loc[len(self.General_Journal)] = Journal_Entry
                for cr, amount in Credits:
                    Journal_Entry = [Date, cr, amount, "Credit"]
                    self.General_Journal.loc[len(self.General_Journal)] = Journal_Entry
            else:
                print("ERROR Creating Journal Entries - Incorrect Number of Amounts")
        elif isinstance(Amount, int) or isinstance(Amount, float):
            Journal_Entry = [Date,DebitAcc, Amount, "Debit"]
            self.General_Journal.loc[len(self.General_Journal)] = Journal_Entry
            Journal_Entry = [Date, CreditAcc, Amount, "Credit"]
            self.General_Journal.loc[len(self.General_Journal)] = Journal_Entry
        else:
            print("ERROR Creating Journal Entry - Incorrect DataTypes")
        self.Data.ConcatData('journal',self.General_Journal)

    def Rev_Record(self,Year,Rev):
        fil = 'rev'
        self.Data.ConcatData('rev',Rev,Year)

    def Rev_Request(self,Year):
        fil = 'rev'
        self.Data.RequestData('rev',Year)

class Inventory_manager:
    def __init__(self,Inv=None):
        self.MasterInventory = {} if Inv == None else Inv

    def ReadInventory(self,product):
        return self.MasterInventory[product]
    
    def UpdateInventory(self,product, New_Inv):
        self.MasterInventory[product] = New_Inv


class Df_manager:
  def __init__(self,SDF=None,PODF=None,EXPDF=None):
    pass
  def Concat(self):
    pass
  def Read(self):
    pass

class Data_manager:
  def __init__(self, GJ=None, IS=None, BS=None, CF=None, Rev=None, PD=None):
    self.MasterGeneralJournal = pd.DataFrame(columns = ["Date","Account","Amount","Balance"]) if GJ == None else GJ
    self.MasterRevenue = {} if Rev == None else Rev
    self.MasterProductData = pd.DataFrame(columns = ["Year","yr_Product","yr_Product_Rev",
                                         "yr_Quantity_Sold","Product_Cost","Selling_Price",
                                         "yr_noRecordsMin","yr_noRecordsMax", "Vendors"]) if PD == None else PD
  def RequestData(self,files, yer = None):
    if 'journal' in files.lower():
      return self.MasterGeneralJournal
    elif 'income' in files.lower():
      pass
    elif 'balance' in files.lower():
      pass
    elif 'cash' in files.lower():
      pass
    elif 'product' in files.lower():
      return self.MasterProductData
    elif 'rev' in files.lower():
      if yer == None:
        print("Error, Missing Year")
      else:
        return self.MasterRevenue[yer]

  def ConcatData(self,files,new_data, yer = None):
    print(files)
    if 'journal' in files.lower():
      self.MasterGeneralJournal = pd.concat([new_data, self.MasterGeneralJournal],ignore_index=True)
    elif 'income' in files.lower():
      pass
    elif 'balance' in files.lower():
      pass
    elif 'cash' in files.lower():
      pass
    elif 'product' in files.lower():
      self.MasterProductData = pd.concat([new_data, self.MasterProductData],ignore_index=True)
    elif 'rev' in files.lower():
      if yer == None:
        print("Error, Missing Year")
      else:
        self.MasterRevenue[yer] = new_data
        print(self.MasterRevenue)

  def PrintData(self,file, Method = None):
    if 'db' in Method.lower():
      pass # Save to Database
    else:
      pass # Print to Terminal