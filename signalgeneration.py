import pandas as pd
from sklearn.linear_model import Lasso
from sklearn.model_selection import train_test_split

f='res_20190614output.csv' #change to a different output file if needed
df=pd.read_csv(f) #read in output
df=df[df['aq0']!=0] #filter two sided market
df=df[df['bq0']!=0]

#topsize - diference in bid/ask quantity at top of book
df['topsize']=df['bq0']-df['aq0']

#spread - top of book bid/ask spread
df['spread']=df['ap0']-df['bp0']

#fivesize - difference in bid/ask quantity for five best levels
df['fivesize']=(df['bq0']+df['bq1']+df['bq2']+df['bq3']+df['bq4']-
               (df['aq0']+df['aq1']+df['aq2']+df['aq3']+df['aq4']))

#topWAP - weighted average price at top of  book
df['topWAP']=(df['bp0']*df['bq0']+df['ap0']*df['aq0'])/(df['bq0']+df['aq0'])

#fiveWAP - weighted average price five levels deep
df['fiveWAP']=((df['bp0']*df['bq0']+df['bp1']*df['bq1']+df['bp2']*df['bq2']+df['bp3']*df['bq3']+df['bp4']*df['bq4']+
               df['ap0']*df['aq0']+df['ap1']*df['aq1']+df['ap2']*df['aq2']+df['ap3']*df['aq3']+df['ap4']*df['aq4'])/
               (df['bq0']+df['bq1']+df['bq2']+df['bq3']+df['bq4']+df['aq0']+df['aq1']+df['aq2']+df['aq3']+df['aq4']))

#book pressure - theoretical price based on top of book; topWAP variant
df['pressure']=(df['bp0']*df['aq0']+df['ap0']*df['bq0'])/(df['bq0']+df['aq0'])

#imbalance - hypothesized in Lipton et. al as predictive of price action; see page two https://arxiv.org/pdf/1312.0514.pdf
df['imbalance']=(df['bq0']-df['aq0'])/(df['bq0']+df['aq0'])

x=df.iloc[:,23:] #predictors
y=df['bp0'] #target

xtrain,xtest,ytrain,ytest=train_test_split(x,y,test_size=0.9,random_state=42) #divide dataset

lasso=Lasso(max_iter=1000) #initialize lasso
lasso.fit(xtrain,ytrain) #train model

print('coefficients:')
print(lasso.coef_)
print('r squared:')
print(lasso.score(xtest,ytest))

#generate trading signal
df['buy']=(lasso.predict(x)+5-df['ap0'])>0.2 #if predicted price is 0.2 points above ap0, lift offer. +5 to correct for training on bp0
df['sell']=(df['bp0']-lasso.predict(x))>0.4 #if predicated price is 0.4 points below bp0, hit bid

df.to_csv(f)