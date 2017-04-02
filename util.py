#--------------------------------------------------------------------#
#util V1.2
#Created, Written, Developed and Designed by Sebastian Sherry April 2016
#This program is licensed under the GNU General Public License v3.0
#--------------------------------------------------------------------#
#Utility functions for the Pycountant program
from datetime import *

#removes any string formatting (eg $) from an entry
def CleanEntry(entry):
    for x in ['Debt','Credit']:
        entry[x] = str(entry[x]).replace('$','')
        entry[x] = str(entry[x]).replace('-','0')
    entry['Date'] = ToDateStringDB(entry['Date'])
    return entry

def GetCurrentDateFormatted(reversed = False):
    date = datetime.now()
    day = str(date.day)
    mon = str(date.month)
    if (len(day) == 1):
        day = "0"+day
    if (len(mon) == 1):
        mon = "0"+mon

    dateStr = ''
    if reversed == False:
        dateStr = str(date.year)+"/"+mon+"/"+day
    else:
        dateStr = day+"/"+mon+"/"+str(date.year)
    return dateStr


#simplied string to datetime conversion
def ToDateTime(string):
    strSplit = string.split('/')
    if (int(strSplit[2]) < 2000):
        strSplit[2] = (int(strSplit[2])+2000)
    print(strSplit)
    date = datetime(int(strSplit[2]),int(strSplit[1]),int(strSplit[0]))
    return date

#same as ToDateTime but for a different input pattern
def ToDateTimeReversed(string):
    strSplit = string.split('/')
    date = datetime(int(strSplit[0]),int(strSplit[1]),int(strSplit[2]))
    return date

#converts a datetime object to a string
def DateToString(date,reverse = False):
    day = str(date.day)
    mon = str(date.month)
    if (len(day) == 1):
        day = "0"+day
    if (len(mon) == 1):
        mon = "0"+mon

    dateStr = ""
    if reverse:
        dateStr = day+"/"+mon+"/"+str(date.year)
    else:
        dateStr = str(date.year)+"/"+mon+"/"+day
    return dateStr

#Combines ToDateTime and DateToString for Database use
def ToDateStringDB(string):
    try:
        date = ToDateTime(string)
    except:
        print("Reversed date")
        date= ToDateTimeReversed(string)
    dateStr = DateToString(date)
    return dateStr

#Combines ToDateTime and DateToString for GUI use
def ToDateStringGUI(string):
    date = ToDateTime(string)
    dateStr = DateToString(date, True)
    return dateStr

#Formats the budget entry for GUI use
def FormatEntry(entry):
    for x in ['Debt','Credit','Bal']:
        if (entry[x] == 0):
            entry[x] = "-"
        else:
            entry[x] = float(entry[x])
        entry[x] = "$"+str(entry[x])
    entry['Date'] = FixDate(entry['Date'])
    return entry

#Formats a week summary for GUI use
#pre: dictionary
#post: list
def FormatSummary(entry):
    for x in ['Debt','Credit','Split']:
        if (entry[x] == 0):
            entry[x] = "-"
        else:
            entry[x] = "${0:.2f}".format(float(entry[x])/100.0)

    return entry


#Converts a list to an dictionary
def ToDict(entry):
    print(entry)
    #force date formatting
    date = ToDateStringGUI(entry[0])
    dic = []
    if len(entry) == 7:
        dic = dict(ID=entry[5], Date=date, Description=entry[1], Debt=entry[2], Credit=entry[3],Ord=entry[6])
    else:
        dic = dict(ID=entry[4], Date=date, Description=entry[1], Debt=entry[2], Credit=entry[3],Ord=entry[5])
    return dic

#converts all the entries values from cents to dollars
def CentsToDollars(entry):
    for col in ['Debt','Credit','Bal']:
        try:
            temp = float(entry[col])/100.0
            entry[col] = "{0:.2f}".format(temp)
        except:
            pass
    return entry

def DollarsToCents(entry):
    for col in ['Debt','Credit']:
        entry[col] = int(float(entry[col])*100)
    return entry

def FixDate(date):
    dateSplit = date.split('/')
    if int(dateSplit[0]) > 2000:
        dateSplit[0] = str(int(dateSplit[0])-2000)
    return dateSplit[2]+"/"+dateSplit[1]+"/"+dateSplit[0]
