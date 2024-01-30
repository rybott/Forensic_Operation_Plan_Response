import pandas as pd

class PreProcessing:
  def __init__(self, product_df, year, Year_Rev):
    self.revenue = Year_Rev[1]
    self.products = product_df
    self.year = year

  def ProductProcessing(self):
    self.product_id_list = self.products['ProductID']
    initial_inventory = self.products[['Product','Initial_Inventory']].to_dict(orient='records')
    self.initial_inventory_dict = {d['Product']:d['Initial_Inventory'] for d in initial_inventory}

    self.product_cost_info = self.products[['Product', 'Vendor','Spread',
                                            'Unit_Price', 'Unit_Cost',
                                            'PerInvoiceRng_Min',
                                            'PerInvoiceRng_Max']].sort_values(by='Spread', ascending=False)
    product_cost = self.product_cost_info
    Rev = self.revenue
    yr_Product_Rev = []
    yr_Quantity_Sold = []
    Product_Cost = []
    Selling_Price = []
    yr_Product = []
    yr_noRecords_min = []
    yr_noRecords_max = []
    vendors = []
    for product in self.product_cost_info['Product']:
      vendor = product_cost[product_cost['Product']==product]['Vendor']
      noRecords_min = product_cost[product_cost['Product']==product]['PerInvoiceRng_Min']
      noRecords_max = product_cost[product_cost['Product']==product]['PerInvoiceRng_Max']
      spread = product_cost[product_cost['Product']==product]['Spread'].item()
      unit_price = product_cost[product_cost['Product']==product]['Unit_Price'].item()
      unit_cost = product_cost[product_cost['Product']==product]['Unit_Cost'].item()
      price_sold = self.revenue * spread
      q_sold = round(price_sold / unit_price,0)
      p_sold = q_sold*unit_price
      if Rev >= p_sold:
        Rev = Rev - p_sold
      else:
        q_sold = round(Rev / unit_price,0)
        p_sold = q_sold*unit_price

      vendors.append(vendor)
      yr_Product.append(product)
      yr_Product_Rev.append(p_sold)
      yr_Quantity_Sold.append(q_sold)
      Product_Cost.append(unit_cost)
      Selling_Price.append(unit_price)
      yr_noRecords_min.append(noRecords_min)
      yr_noRecords_max.append(noRecords_max)

    processed_product_lists = [yr_Product, yr_Product_Rev,
                               yr_Quantity_Sold, Product_Cost, Selling_Price,
                               yr_noRecords_min, yr_noRecords_max, vendors]

    self.Processed_Product_df = pd.DataFrame(processed_product_lists).T
    self.Processed_Product_df.columns = ["yr_Product","yr_Product_Rev",
                                         "yr_Quantity_Sold","Product_Cost","Selling_Price",
                                         "yr_noRecordsMin","yr_noRecordsMax", "Vendors"]
    return [self.year, self.Processed_Product_df, self.initial_inventory_dict]