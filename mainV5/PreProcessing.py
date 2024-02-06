import pandas as pd

class PreProcessing:
  def __init__(self, RevDF, product_df):
    # self.YrRev_Dict = {d['Year']:d['Rev'] for d in RevDF}
    self.YrRev_DictList = RevDF[['Year','Rev']].to_dict(orient='records')
    self.products = product_df

  def ProductProcessing(self):
    self.product_id_list = self.products['ProductID']
    initial_inventory = self.products[['Product', 'Initial_Inventory']].to_dict(orient='records')
    self.initial_inventory_dict = {d['Product']:d['Initial_Inventory'] for d in initial_inventory}
    self.product_cost_info = self.products[['Product', 'Vendor','Spread',
                                            'Unit_Price', 'Unit_Cost',
                                            'PerInvoiceRng_Min',
                                            'PerInvoiceRng_Max']].sort_values(by='Spread', ascending=False)
    Products = self.product_cost_info
    list_yrlyProduct_data = []
    for YrRev in self.YrRev_DictList:
      Year = YrRev['Year']
      Rev = YrRev['Rev']
      for product in self.product_cost_info['Product']:
        self.Processed_list = Products[Products['Product']==product].copy()
        spread = self.Processed_list['Spread'].values[0]
        unit_price = self.Processed_list['Unit_Price'].values[0]
        unit_cost = self.Processed_list['Unit_Cost'].values[0]
        division_of_rev = Rev * spread
        q_sold = round(division_of_rev / unit_price,0)
        p_sold = q_sold*unit_price
        New_Rev = p_sold
        self.Processed_list.loc[:,'q_sold'] = q_sold
        self.Processed_list.loc[:,'Product_Rev'] = New_Rev
        self.Processed_list.loc[:,'Year'] = Year
        list_yrlyProduct_data.append(self.Processed_list.values.tolist()[0])
    YrlyProduct_Data_df = pd.DataFrame(list_yrlyProduct_data,
                                       columns = ['Product', 'Vendor','Spread',
                                            'Unit_Price', 'Unit_Cost',
                                            'PerInvoiceRng_Min',
                                            'PerInvoiceRng_Max', 'q_sold',
                                            'Total_Product_Rev','Year'])
    return [YrlyProduct_Data_df,self.initial_inventory_dict]