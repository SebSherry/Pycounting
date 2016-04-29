#--------------------------------------------------------------------#
#Budget_calc V1.2
#Created, Written, Developed and Designed by Sebastian Sherry April 2016
#This program is licensed under the GNU General Public License v3.0
#--------------------------------------------------------------------#
from db import *
from util import *
import datetime

#filenames
filen = "budget.db"

budget = []

#Returns the daily budget
#def GetDailyBudget():
#    global budget
#    if budget == []:
#        budget = Database(filename = filen, table='daily')
#    tempList = []
#    for entry in budget:
#        entry = CentsToDollars(entry)
#        tempList.append(entry)
#    listBudget = orderBudget(tempList)
#    return listBudget

#Returns the daily budget
def GetDailyBudget():
    global budget
    if budget == []:
        budget = Database(filename = filen, table='daily')
    return FillBudgetList(True)

def GetWeeklySummary():
    if budget != []:
        #variables
        summarys = []
        datesInWeek = []
        weekLists = []
        dates = budget.getDates(True)
        weekStart = ToDateTimeReversed(dates[0])
        datesInWeek.append(weekStart)

        #seperate all dates into weeks
        for date in dates:
            #format date
            date = ToDateTimeReversed(date)
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
                date = DateToString(date)
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
            endDate = ToDateStringGUI(str(endDate.day)+"/"+str(endDate.month)+"/"+str(endDate.year))
            startDate = ToDateStringGUI(str(week[0].day)+"/"+str(week[0].month)+"/"+str(week[0].year))
            weekString = startDate+" - "+endDate
            #add weekly summary to summarys
            tempSum = dict(Week = weekString, Debt = debt, Credit = credit, Split = split)
            summarys.append(FormatSummary(tempSum))
        #end for
        return summarys
    #else return empty list
    else:
        return []

def FillBudgetList(toCents):
    tempList = []
    listBudget = []
    dates = budget.getDates()
    for date in dates:
        tempList = budget.retrieveEntriesInOrder(date)
        for entry in tempList:
            if toCents == True:
                entry = CentsToDollars(entry)

            listBudget.append(entry)
    return listBudget

#Updates the balance section of the daily budget
def GenBalance():
    global budget
    #budget in list format
    budList = FillBudgetList(False)

    #create list of dictionarys to hold balances
    balances = []
    #do the first entry
    bal = float(budList[len(budList)-1]['Credit'])-float(budList[len(budList)-1]['Debt'])
    dic = dict(ID=budList[len(budList)-1]['ID'],BAL=bal)
    balances.append(dic)

    #loop over the list from the 2nd entry onwards
    for x in range(1,len(budList)):
        i = (len(budList)-1)-x
        bal = balances[x-1]['BAL']+(float(budList[i]['Credit'])-float(budList[i]['Debt']))
        dic = dict(ID=budList[i]['ID'],BAL=bal)
        balances.append(dic)

    for bal in balances:
        bal['BAL'] = bal['BAL']/100
    #return list of balances
    return balances

#Adds an entry to the budget
def AddEntry(entry):
    global budget
    #Clear Formatting
    CleanEntry(entry)
    entry = DollarsToCents(entry)
    #add entry
    budget.insert(entry)
    #update the balance column
    #UpdateBalance(index)

#updates changed values in an entry
#original = entry before modification
#altered = entry after modification
def EditEntry(original,altered):
    original = DollarsToCents(original)
    altered = DollarsToCents(altered)
    for col in ['Date','Description','Debt','Credit']:
        if original[col] != altered[col]:
            budget.update(altered, col)
    return True

#Removes entry from budget
def RemoveEntry(entry):
    budget.delete(entry['ID'])
    return True

#reorganizes the budget list by date and by order of entry
def orderBudget(tempList):
    global budget
    dates = budget.getDates()
    budList = []
    for date in dates:
        temp = []
        for entry in tempList:
            if entry['Date'] == date:
                temp.append(entry)
        budList += sortDates(temp)
    return budList

def checkDate(entry):
    if entry['Date'][0] == '4':
        entry = FixDate(entry)
        budget.update(entry, 'Date')

def swapEntries(firstEnt,secondEnt):
    global budget
    temp = firstEnt['Ord']
    firstEnt['Ord'] = secondEnt['Ord']
    secondEnt['Ord'] = temp
    budget.update(firstEnt, 'Ord')
    budget.update(secondEnt, 'Ord')
    return True
