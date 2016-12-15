
# coding: utf-8

# ---
# 
# _You are currently looking at **version 1.1** of this notebook. To download notebooks and datafiles, as well as get help on Jupyter notebooks in the Coursera platform, visit the [Jupyter Notebook FAQ](https://www.coursera.org/learn/python-data-analysis/resources/0dhYG) course resource._
# 
# ---

# In[1]:

import pandas as pd
import numpy as np
from scipy.stats import ttest_ind


# # Assignment 4 - Hypothesis Testing
# This assignment requires more individual learning than previous assignments - you are encouraged to check out the [pandas documentation](http://pandas.pydata.org/pandas-docs/stable/) to find functions or methods you might not have used yet, or ask questions on [Stack Overflow](http://stackoverflow.com/) and tag them as pandas and python related. And of course, the discussion forums are open for interaction with your peers and the course staff.
# 
# Definitions:
# * A _quarter_ is a specific three month period, Q1 is January through March, Q2 is April through June, Q3 is July through September, Q4 is October through December.
# * A _recession_ is defined as starting with two consecutive quarters of GDP decline, and ending with two consecutive quarters of GDP growth.
# * A _recession bottom_ is the quarter within a recession which had the lowest GDP.
# * A _university town_ is a city which has a high percentage of university students compared to the total population of the city.
# 
# **Hypothesis**: University towns have their mean housing prices less effected by recessions. Run a t-test to compare the ratio of the mean price of houses in university towns the quarter before the recession starts compared to the recession bottom. (`price_ratio=quarter_before_recession/recession_bottom`)
# 
# The following data files are available for this assignment:
# * From the [Zillow research data site](http://www.zillow.com/research/data/) there is housing data for the United States. In particular the datafile for [all homes at a city level](http://files.zillowstatic.com/research/public/City/City_Zhvi_AllHomes.csv), ```City_Zhvi_AllHomes.csv```, has median home sale prices at a fine grained level.
# * From the Wikipedia page on college towns is a list of [university towns in the United States](https://en.wikipedia.org/wiki/List_of_college_towns#College_towns_in_the_United_States) which has been copy and pasted into the file ```university_towns.txt```.
# * From Bureau of Economic Analysis, US Department of Commerce, the [GDP over time](http://www.bea.gov/national/index.htm#gdp) of the United States in current dollars (use the chained value in 2009 dollars), in quarterly intervals, in the file ```gdplev.xls```. For this assignment, only look at GDP data from the first quarter of 2000 onward.
# 
# Each function in this assignment below is worth 10%, with the exception of ```run_ttest()```, which is worth 50%.

# In[2]:

# Use this dictionary to map state names to two letter acronyms
states = {'OH': 'Ohio', 'KY': 'Kentucky', 'AS': 'American Samoa', 'NV': 'Nevada', 'WY': 'Wyoming', 'NA': 'National', 'AL': 'Alabama', 'MD': 'Maryland', 'AK': 'Alaska', 'UT': 'Utah', 'OR': 'Oregon', 'MT': 'Montana', 'IL': 'Illinois', 'TN': 'Tennessee', 'DC': 'District of Columbia', 'VT': 'Vermont', 'ID': 'Idaho', 'AR': 'Arkansas', 'ME': 'Maine', 'WA': 'Washington', 'HI': 'Hawaii', 'WI': 'Wisconsin', 'MI': 'Michigan', 'IN': 'Indiana', 'NJ': 'New Jersey', 'AZ': 'Arizona', 'GU': 'Guam', 'MS': 'Mississippi', 'PR': 'Puerto Rico', 'NC': 'North Carolina', 'TX': 'Texas', 'SD': 'South Dakota', 'MP': 'Northern Mariana Islands', 'IA': 'Iowa', 'MO': 'Missouri', 'CT': 'Connecticut', 'WV': 'West Virginia', 'SC': 'South Carolina', 'LA': 'Louisiana', 'KS': 'Kansas', 'NY': 'New York', 'NE': 'Nebraska', 'OK': 'Oklahoma', 'FL': 'Florida', 'CA': 'California', 'CO': 'Colorado', 'PA': 'Pennsylvania', 'DE': 'Delaware', 'NM': 'New Mexico', 'RI': 'Rhode Island', 'MN': 'Minnesota', 'VI': 'Virgin Islands', 'NH': 'New Hampshire', 'MA': 'Massachusetts', 'GA': 'Georgia', 'ND': 'North Dakota', 'VA': 'Virginia'}


# In[13]:

def get_list_of_university_towns():
    '''Returns a DataFrame of towns and the states they are in from the 
    university_towns.txt list. The format of the DataFrame should be:
    DataFrame( [ ["Michigan", "Ann Arbor"], ["Michigan", "Yipsilanti"] ], 
    columns=["State", "RegionName"]  )
    
    The following cleaning needs to be done:

    1. For "State", removing characters from "[" to the end.
    2. For "RegionName", when applicable, removing every character from " (" to the end.
    3. Depending on how you read the data, you may need to remove newline character '\n'. '''
    data = pd.read_table('university_towns.txt',sep='\n',names=['name'])
    state = ''
    
    def clean(r):
        global state
        Region = ''
        if '[edit]' in r:
            state = r.split('[')[0]
        elif '(' in r:
            Region = r.split(' (')[0]
        else:
            Region = r
        return pd.Series({'State':state, 'RegionName': Region})
    #merge new date 
    data = data.merge(data['name'].apply(clean),right_index=True,left_index=True)
    data = data[data['RegionName'] != '']
    data = data.reset_index()
    data = data.loc[:,['State', 'RegionName']]
    return data
get_list_of_university_towns()


# In[27]:

def get_gdp():
    gdp = pd.read_excel('gdplev.xls',skiprows=5)
    gdp = gdp.loc[214:,['Unnamed: 4','GDP in billions of chained 2009 dollars.1']]
    gdp.columns = ['year/q' , 'gdp']
    gdp = gdp.reset_index().drop('index',axis='columns')
    return gdp

def get_housing_data():
    data = pd.read_csv('City_Zhvi_AllHomes.csv')
    return data


# In[28]:

def get_recession_start():
    '''Returns the year and quarter of the recession start time as a 
    string value in a such as 2005q3'''
    
    gdp = get_gdp().copy()
    alist = []
    for i in gdp.index:
        if (gdp.gdp.iloc[i-1]) > (gdp.gdp.iloc[i]) > (gdp.gdp.iloc[i+1]):
            alist.append(i)
    return gdp['year/q'][alist[0]]
get_recession_start()


# In[33]:

def get_recession_end():
    '''Returns the year and quarter of the recession end time as a 
    string value in a format such as 2005q3'''
    gdp = get_gdp().copy()
    for i in gdp.index[32:]:
        if (gdp.gdp.iloc[i+1]) > (gdp.gdp.iloc[i]) > (gdp.gdp.iloc[i-1]):
            x = i
            break
    return gdp['year/q'][x+1]
get_recession_end()


# In[34]:

def get_recession_bottom():
    '''Returns the year and quarter of the recession bottom time as a 
    string value in a format such as 2005q3'''
    gdp = get_gdp().copy()
    bott = min(gdp['gdp'][34:40])
    a = gdp[gdp['gdp']== bott] 
    return a['year/q'][37]
get_recession_bottom()


# In[38]:

def new_col_names():
    #generating the new coloumns names 
    years = list(range(2000,2017))
    quars = ['q1','q2','q3','q4']
    quar_years = []
    for i in years:
        for x in quars:
            quar_years.append((str(i)+x))
    return quar_years[:67]


# In[39]:

def convert_housing_data_to_quarters():
    '''Converts the housing data to quarters and returns it as mean 
    values in a dataframe. This dataframe should be a dataframe with
    columns for 2000q1 through 2016q3, and should have a multi-index
    in the shape of ["State","RegionName"].
    
    Note: Quarters are defined in the assignment description, they are
    not arbitrary three month periods.
    
    The resulting dataframe should have 67 columns, and 10,730 rows.
    '''
    data = get_housing_data().copy()
    data.drop(['Metro','CountyName','RegionID','SizeRank'],axis=1,inplace=1)
    data['State'] = data['State'].map(states)
    data.set_index(['State','RegionName'],inplace=True)
    col = list(data.columns)
    col = col[0:45]
    data.drop(col,axis=1,inplace=1)

    #qs is the quarters of the year
    qs = [list(data.columns)[x:x+3] for x in range(0, len(list(data.columns)), 3)]
    # new columns
    column_names = new_col_names()
    for col,q in zip(column_names,qs):
        data[col] = data[q].mean(axis=1)
        
    data = data[column_names]
    return data
convert_housing_data_to_quarters()


# In[41]:

def run_ttest():
    '''First creates new data showing the decline or growth of housing prices
    between the recession start and the recession bottom. Then runs a ttest
    comparing the university town values to the non-university towns values, 
    return whether the alternative hypothesis (that the two groups are the same)
    is true or not as well as the p-value of the confidence. 
    
    Return the tuple (different, p, better) where different=True if the t-test is
    True at a p<0.01 (we reject the null hypothesis), or different=False if 
    otherwise (we cannot reject the null hypothesis). The variable p should
    be equal to the exact p value returned from scipy.stats.ttest_ind(). The
    value for better should be either "university town" or "non-university town"
    depending on which has a lower mean price ratio (which is equivilent to a
    reduced market loss).'''
    data = convert_housing_data_to_quarters().copy()
    data = data.loc[:,'2008q3':'2009q2']
    data = data.reset_index()
    def diff(row):
        return row['2008q3'] - row['2009q2']
    
    data['up&down'] = data.apply(diff,axis=1)
    #uni data 
    
    uni = get_list_of_university_towns()['RegionName']
    uni = set(uni)

    def is_nui_town(row):
        #check if the town is a university towns or not.
        if row['RegionName'] in uni:
            return 1
        else:
            return 0
    data['is_uni'] = data.apply(is_nui_town,axis=1)
    
    
    not_uni = data[data['is_uni']==0].loc[:,'up&down'].dropna()
    is_uni  = data[data['is_uni']==1].loc[:,'up&down'].dropna()
    def better():
        if not_uni.mean() < is_uni.mean():
            return 'non-university town'
        else:
            return 'university town'
    p_val = list(ttest_ind(not_uni, is_uni))[1]
    result = (True,p_val,better())
    
    return result
run_ttest()


# In[ ]:



