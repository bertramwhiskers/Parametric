import pandas as pd
from sortedcontainers import SortedDict

updates=pd.read_csv('res_20190614.csv') #read in provided updates

file=open('res_20190614output.csv', 'w') #create CSV; change if you want to work with a different input file
file.write('timestamp,price,side,bp0,bq0,bp1,bq1,bp2,bq2,bp3,bq3,bp4,bq4,ap0,aq0,ap1,aq1,ap2,aq2,ap3,aq3,ap4,aq4\n') #header in requested format

#bids and asks will be kept in two separate sorted dictionaries as price:quantity
bids=SortedDict()
asks=SortedDict()

def add(update):
  #using try/except instead of if/then because number of records greatly exceeds unique prices
  try:
    book[update.price]+=update.quantity #book is a reference to bids or asks
  except KeyError:
    book.update({update.price:update.quantity})
    #SortedDict.update() works like bisect.insort, automatically maintains increasing order
def delete(update):
  book[update.price]-=update.quantity

def modify(update):
  #delete previous update with same id, add current update
  delete(updates[:update.Index][updates.id==update.id].iloc[-1]) #filter dataframe for same id
  add(update)

def clean(side):
  #remove price levels with zero quantity
  if side==bids:
    delindex = book.keys()[-1] #best bid is last in dict
    bestindex=-1
  else:
    delindex = book.keys()[0] #best offer is first in dict
    bestindex=0

  if book.values()[bestindex] == 0: #if no quantity at TOB, delete
    del book[delindex] 

def updatetofile(update):
  s = str(update.timestamp) + ',' + str(update.price) + ',' + str(update.side)
  #write bids
  for x in range(1, 6):
    try:
      temps = ',' + str(list(bids)[-x]) + ',' + str(list(bids.values())[-x]) #highest bids are at end of dict
    except IndexError:
      temps = ',0,0'
    s += temps
  #write asks
  for y in range(5):
    try:
      temps = ',' + str(list(asks)[y]) + ',' + str(list(asks.values())[y]) #lowest offers are at start of dict
    except IndexError:
      temps = ',0,0'
    s += temps

  s += '\n'
  file.write(s)

for update in updates.itertuples():

  if update.side=='b': book=bids #reference side
  else: book=asks

  #add update to book
  if update.action=='a': add(update) 
  elif update.action=='d': delete(update)
  else: modify(update)

  #remove zero quantity levels
  clean(book)
  #write to file
  updatetofile(update)
  
file.close()