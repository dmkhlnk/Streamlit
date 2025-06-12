import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
salary  = pd.read_excel('/Salary.xlsx')
inflation = pd.read_excel('/Inflation_rate.xlsx')
salary = salary.transpose().reset_index()
salary = salary.rename({'index':'year', 0:'Добыча полезных ископаемых', 1:'Строительство', 2:'Образование'}, axis =1)
salary = salary.drop(index=0)
inflation_2016 = inflation[inflation['year']>=2016]
inflation_before_2016 = inflation[inflation['year']<2016]
inflation.head()


def cpi(inflation):
    inflation = list(inflation)
    for i in range(len(inflation)):
        if i == 0:
            inflation[i] = 1
        else:
            cpi = inflation[i - 1] * (1 + inflation[i] / 100)
            inflation[i] = cpi
    return inflation

inflation_2016['cpi'] = cpi(inflation_2016['inflation_rate'])


def discount(inflation):
    inflation = list(inflation)
    for i in range(len(inflation)):
        if i == 0:
            discount_rate = (1 + inflation[i] / 100)
            cpi = (1 / discount_rate)
            inflation[i] = cpi
        else:
            discount_rate = discount_rate * (1 + inflation[i] / 100)
            cpi = 1 / discount_rate
            inflation[i] = cpi
    return inflation

inflation_before_2016 = inflation_before_2016.sort_values(by = 'year', ascending=False)
inflation_before_2016['cpi'] = discount(inflation_before_2016['inflation_rate'])

inflation_before_2016 = inflation_before_2016.sort_values(by = 'year', ascending=True)
inflation = pd.concat([inflation_2016, inflation_before_2016]).sort_values(by = 'year', ascending = True)
inflation = inflation[inflation['year']>=2000].reset_index()

salary = salary.merge(inflation[['year', 'cpi']], on = 'year', how = 'inner')

salary['Minearal_mining_adj'] = salary['Добыча полезных ископаемых']/salary['cpi']
salary['Construction_adj'] = salary['Строительство']/salary['cpi']
salary['Education_adj'] = salary['Образование']/salary['cpi']

