#--------------------------------------------------------------------#
#Budget_calc V1.5
#Created, Written, Developed and Designed by Sebastian Sherry April 2016
#This program is licensed under the GNU General Public License v3.0
#--------------------------------------------------------------------#
try:
    import db as db
    import util as util
except:
    import Pycounting.db as db
    import Pycounting.util as util

#from DataHandler.db import Database
import datetime
import logging

filen = 'pycounting.db'

budget = []

"""Creates a connection to the SQL db"""
def connect():
    budget = []
    try:
        budget = db.Database(filename = filen, table='daily')
    except:
        budget = db.Database(filename = filenAlt, table='daily')
    return budget

"""Returns budget as a list of dictionarys"""
def GetDailyDict():
    global budget
    budget = connect()
    #balances = GenBalance()
    budgetList = budget.retrieveAll()
    if (len(budgetList) == 0):
        return []
    budgetList = orderBudget(budgetList)
    budgetList = GenBalance(budgetList)
    for entry in budgetList:
        entry = util.FormatEntry(util.CentsToDollars(entry))
    return budgetList

#Returns the daily budget
def GetDailyBudget():
    global budget
    budget = connect()
    return FillBudgetList(True)

def GetWeeklySummary():
    #variables
    summarys = []
    datesInWeek = []
    weekLists = []
    dates = budget.getDates(True)
    print(dates)
    #If there are dates, there must be entries
    #Thus if entries is not empty, then a summarry can be formed
    if dates != []:
        weekStart = util.ToDateTimeReversed(dates[0])
        datesInWeek.append(weekStart)

        #seperate all dates into weeks
        for date in dates:
            #format date
            date = util.ToDateTimeReversed(date)
            #if the date is not the starting date and the difference between the two is less than or equal to 6 days
            if abs((date - weekStart).days) <= 6:
                if date not in datesInWeek:
                    datesInWeek.append(date)
            else:
                weekLists.append(datesInWeek)
                weekStart = weekStart + datetime.timedelta(days=7)
                datesInWeek = [weekStart]
                #check for skipped weeks
                if abs((date - weekStart).days) > 6:
                    found = False
                    while(not found):
                        datesInWeek.append(weekStart + datetime.timedelta(days=6))
                        weekLists.append(datesInWeek)
                        weekStart = weekStart + datetime.timedelta(days=7)
                        datesInWeek = [weekStart]
                        if abs(date - weekStart).days <= 6:
                            found = True
                    #end if and while
                if date not in datesInWeek:
                    datesInWeek.append(date)
        #end for
        #create summarys
        for week in weekLists:
            debt = 0
            credit = 0
            split = 0
            #get each entry for date in week
            for date in week:
                date = util.DateToString(date)
                #grab entries for date
                tempList = budget.retrieveEntriesInOrder(date)
                #update debt and credit
                for entry in tempList:
                    if int(entry['Debt']) != 0:
                        debt += int(entry['Debt'])
                    else:
                        credit += int(entry['Credit'])
            #calculate split
            split = credit - debt
            #get start and end dates
            endDate = week[0] + datetime.timedelta(days=6)
            endDate = util.ToDateStringGUI(str(endDate.day)+"/"+str(endDate.month)+"/"+str(endDate.year))
            startDate = util.ToDateStringGUI(str(week[0].day)+"/"+str(week[0].month)+"/"+str(week[0].year))
            weekString = startDate+" - "+endDate
            #add weekly summary to summarys
            tempSum = dict(Week = weekString, Debt = debt, Credit = credit, Split = split)
            summarys.append(util.FormatSummary(tempSum))
        #end for
        return summarys
    #else return empty list
    else:
        return []

def FillBudgetList(toCents):
    global budget
    budget = connect()
    tempList = []
    listBudget = []
    dates = budget.getDates()
    for date in dates:
        tempList = budget.retrieveEntriesInOrder(date)
        for entry in tempList:
            if toCents == True:
                entry = util.CentsToDollars(entry)
            listBudget.append(entry)
    return listBudget

#Updates the balance section of the daily budget
def GenBalance(budList):
    tempList = []
    #do the first entry
    bal = {'Bal': float(budList[len(budList)-1]['Credit'])-float(budList[len(budList)-1]['Debt'])}
    budList[len(budList)-1].update(bal)
    tempList.append(budList[len(budList)-1])
    #print(budList[len(budList)-1])
    #loop over the list from the 2nd entry onwards
    for x in range(1,len(budList)):
        i = (len(budList)-1)-x
        entry = budList[i]
        #print(entry)
        #print(budList[x-1])
        bal = tempList[x-1]['Bal']+(float(entry['Credit'])-float(entry['Debt']))
        temp = dict(ID=entry['ID'], Date=entry['Date'], Description=entry['Description'], Debt=entry['Debt'], Credit=entry['Credit'],Ord=entry['Ord'], Bal=bal)
        tempList.append(temp)
    #return list of balances
    tempList.reverse()
    return tempList

#Adds an entry to the budget
def AddEntry(entry):
    global budget
    budget = connect()
    entry['Ord'] = len(FillBudgetList(False))

    #Clear Formatting
    util.CleanEntry(entry)

    #Dollars to cents
    util.DollarsToCents(entry)

    #add entry
    budget.insert(entry)

    #update the balance column
    #UpdateBalance(index)

#updates changed values in an entry
#original = entry before modification
#altered = entry after modification
def EditEntry(original,altered):
    original = util.DollarsToCents(util.CleanEntry(original))
    altered = util.DollarsToCents(util.CleanEntry(altered))
    for col in ['Date','Description','Debt','Credit']:
        if original[col] != altered[col]:
            budget.update(altered, col)
    return True

#Removes entry from budget
def RemoveEntry(entry):
    budget.delete(entry['ID'])
    return True

"""reorganizes the budget list by date and by order of entry"""
def orderBudget(tempList):
    global budget
    dates = budget.getDates()
    budList = []
    for date in dates:
        dateAlt = util.FixDate(date)
        temp = []
        for entry in tempList:
            if entry['Date'] == date or entry['Date'] == dateAlt:
                temp.append(entry)
        budList += sortDates(temp)
    return budList

"""Sorts entries of the same date into credit and debt transactions"""
def sortDates(dateList):
    if len(dateList) == 0: return dateList
    tempCredit = []
    tempDebt = []
    for entry in dateList:
        if entry['Debt'] == 0:
            tempDebt.append(entry)
        else:
            tempCredit.append(entry)
    tempAll = tempCredit + tempDebt
    return tempAll

def checkDate(entry):
    if entry['Date'][0] == '4':
        entry = util.FixDate(entry)
        budget.update(entry, 'Date')

def swapEntries(firstEnt,secondEnt):
    global budget
    if firstEnt['Date'] != secondEnt['Date']: return False
    budget = connect()
    temp = firstEnt['Ord']
    firstEnt['Ord'] = secondEnt['Ord']
    secondEnt['Ord'] = temp
    budget.update(firstEnt, 'Ord')
    budget.update(secondEnt, 'Ord')
    return True

def getSingleEntry(ID):
    global budget
    if budget == []: budget = connect()
    entry = util.CentsToDollars(budget.retrieve("ID",ID))
    dateSplit = entry['Date'].split('/')
    entry['Date'] = dateSplit[2]+"/"+dateSplit[1]+"/"+dateSplit[0]
    return entry

def getMostRecentCredits():
    global budget
    if budget == []: budget = connect()
    credits = budget.retrieveMulti("Description","Weekly Top Up")
    return credits[-1]

if __name__ == "__main__":
    budgetList = GetDailyDict()
    for entry in budgetList:
        print(entry)
    #for x in range(0,10):
    #    print(budgetList[x])
    #swapEntries(budgetList[4],budgetList[5])
    #budgetList = GetDailyDict()
    #for x in range(0,10):
    #    print(budgetList[x])
