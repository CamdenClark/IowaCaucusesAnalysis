
# coding: utf-8

# In[1]:

import pandas as pd
import matplotlib.pyplot as plt
population = pd.read_excel("PopulationEstimates.xls") #First, population
population=population[population['Unnamed: 1'].isin(["IA"])]
population=population[~population['Unnamed: 2'].isin(["Iowa"])]
population=population.drop(population.columns[[x for x in range (3,13)]],axis=1)
population=population.drop(population.columns[[x for x in range (4,74)]],axis=1)
population=population.drop(population.columns[[0,1]],axis=1)
population=population.rename(columns={'Unnamed: 13':'Population','Unnamed: 2':'County'})
population=population.reset_index(drop=True)
population['County']=population['County'].apply(lambda x: x[:-7])
population.set_index("County",drop=True,inplace=True)
population.index.name=None

poverty = pd.read_excel("PovertyEstimates.xls") #Now, poverty
poverty=poverty[poverty['Unnamed: 1'].isin(["IA"])]
poverty=poverty[~poverty['Unnamed: 2'].isin(["Iowa"])]
poverty=poverty.drop(poverty.columns[[x for x in range (3,10)]],axis=1)
poverty=poverty.drop(poverty.columns[[x for x in range (4,27)]],axis=1)
poverty=poverty.drop(poverty.columns[[0,1]],axis=1)
poverty=poverty.rename(columns={'Unnamed: 10':'Poverty Rate','Unnamed: 2':'County'})
poverty=poverty.reset_index(drop=True)
poverty['County']=poverty['County'].apply(lambda x: x[:-7])
poverty.set_index("County",drop=True,inplace=True)
poverty.index.name=None

unemployment = pd.read_excel("Unemployment.xls") #Now, unemployment/median income
unemployment=unemployment[unemployment['Unnamed: 1'].isin(["IA"])]
unemployment=unemployment[~unemployment['Unnamed: 2'].isin(["Iowa"])]
unemployment=unemployment.drop(unemployment.columns[[x for x in range (3,42)]],axis=1)
unemployment=unemployment.drop(unemployment.columns[[x for x in range (5,6)]],axis=1)
unemployment=unemployment.drop(unemployment.columns[[0,1]],axis=1)
unemployment=unemployment.rename(columns={'Unnamed: 42':'Unemployment Rate','Unnamed: 2':'County','Unnamed: 43':'Median Income'})
unemployment=unemployment.reset_index(drop=True)
unemployment['County']=unemployment['County'].apply(lambda x: x[:-11])
unemployment.set_index("County",drop=True,inplace=True)
unemployment.index.name=None


# In[2]:

import urllib.request
import simplejson
test_json=urllib.request.urlopen("https://iowadems-caucussitecdn-prod2.azureedge.net/api/countycandidateresults").read()
json_parsed=simplejson.loads(test_json)
CountyResults=json_parsed['CountyResults']
del CountyResults[-1] #Deleting extraneous information
FinalResults=[[county['County']['Name'],county['Candidates'][2]['WinPercentage'],county['Candidates'][4]['WinPercentage']] for county in CountyResults]
FinalResults=FinalResults
ResultsDF=pd.DataFrame(FinalResults,columns=['County','Hillary Win Pct','Bernie Win Pct'])
ResultsDF=ResultsDF.sort_values(by=['County'])
ResultsDF.set_index("County",drop=True,inplace=True)
ResultsDF.index.name=None


# In[3]:

Final=pd.concat([ResultsDF,population,poverty,unemployment],axis=1,join='inner')


# In[6]:

import numpy as np
from sklearn import linear_model

unemploymentclf = linear_model.LinearRegression()
unemploymentclf.fit(Final['Unemployment Rate'].reshape((99,1)),Final['Hillary Win Pct'].reshape((99,1)))
f,ax=plt.subplots(2,2,sharey='row')
ax[1,1].plot(Final['Unemployment Rate'],Final['Hillary Win Pct'],'ro')
ax[1,1].plot(Final['Unemployment Rate'].reshape((99,1)),unemploymentclf.predict(Final['Unemployment Rate'].reshape((99,1))),color='blue')
ax[1,1].set_title('Unemployment/Clinton Win Pct')

incomefinal=Final[Final['Median Income']<70000]
medianincomeclf = linear_model.LinearRegression()
medianincomeclf.fit(incomefinal['Median Income'].reshape((98,1)),incomefinal['Hillary Win Pct'].reshape((98,1)))
ax[1,0].plot(incomefinal['Median Income'],incomefinal['Hillary Win Pct'],'ro')
ax[1,0].plot(incomefinal['Median Income'].reshape((98,1)),medianincomeclf.predict(incomefinal['Median Income'].reshape((98,1))),color='blue')
ax[1,0].set_title('Median Income/Clinton Win Pct')


clf = linear_model.LinearRegression()
NewFinal=Final[Final['Population']<60000]
clf.fit(NewFinal['Population'].reshape((89,1)),NewFinal['Hillary Win Pct'].reshape((89,1)))
ax[0,0].plot(NewFinal['Population'],NewFinal['Hillary Win Pct'],'ro')
ax[0,0].plot(NewFinal['Population'].reshape((89,1)),clf.predict(NewFinal['Population'].reshape((89,1))),color='blue')
ax[0,0].set_title('Population/Clinton Win Pct')

povertyclf = linear_model.LinearRegression()
povertyclf.fit(Final['Poverty Rate'].reshape((99,1)),Final['Hillary Win Pct'].reshape((99,1)))
ax[0,1].plot(Final['Poverty Rate'],Final['Hillary Win Pct'],'ro')
ax[0,1].plot(Final['Poverty Rate'].reshape((99,1)),povertyclf.predict(Final['Poverty Rate'].reshape((99,1))),color='blue')
ax[0,1].set_title('Poverty Rate/Clinton Win Pct')

f.suptitle("Analyzing Iowa Caucus Data with Census Data")
plt.show()

