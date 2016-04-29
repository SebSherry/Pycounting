#--------------------------------------------------------------------#
#db.py V1.0
#Created, Written, Developed and Designed by Sebastian Sherry April 2016
#This program is licensed under the GNU General Public License v3.0
#--------------------------------------------------------------------#
import sqlite3

from util import *

#---------------------------------------------------------------------------#
#ran once
#db.execute('drop table if exists daily')
#db.execute('create table daily (ID INTEGER PRIMARY KEY NOT NULL, Date text, Description text, Debt int, Credit int)')
filen = 'budget.db'
filename = 'Budget_2016'
#---------------------------------------------------------------------------#

class Database:
    def __init__(self, **kwargs):
        self.filename = kwargs.get('filename')
        self.table = kwargs.get('table')

    @property
    def filename(self): return self._filename

    @filename.setter
    def filename(self, fn):
        self._filename = fn
        self._db = sqlite3.connect(fn)
        self._db.row_factory = sqlite3.Row

    @property
    def table(self): return self._table

    @filename.setter
    def table(self, tb):
        self._table = tb
        self._db.execute('create table IF NOT EXISTS daily (ID INTEGER PRIMARY KEY NOT NULL, Date text, Description text, Debt int, Credit int, Ord int NOT NULL)')

    def insert(self, row):
        self._db.execute('insert into {} (Date, Description, Debt, Credit, Ord) values (?,?,?,?,?)'.format(self._table),(row['Date'], row['Description'], row['Debt'], row['Credit'], row['Ord']))
        self._db.commit()

    def retrieve(self, key):
        cursor = self._db.execute('select * from {} where ID = ?'.format(self._table), (key,))
        return dict(cursor.fetchone())

    def retrieveMulti(self, col, key):
        cursor = self._db.execute('select * from {} where {} = ?'.format(self._table), col, (key,))
        entries = []
        for row in cursor:
            entries.append(dict(row))
        return entries

    def retrieveEntriesInOrder(self, key):
        cursor = self._db.execute('select * from {} where Date = ? Order by Ord DESC'.format(self._table), (key,))
        entries = []
        for row in cursor:
            entries.append(dict(row))
        return entries

    def getDates(self, reverse = False):
        order = 'DESC'
        if reverse:
            order = 'ASC'
        cursor = self._db.execute('select distinct Date from {} order by DATE {}'.format(self._table, order))
        dates = []
        for date in cursor:
            #returns date as a sting element list. Then converted to string
            temp = list(date)
            dates.append(temp[0])
        return dates

    def update(self,row, col):
        self._db.execute('update {} set {} = ? where ID = ?'.format(self._table, col),(row[col], row['ID']))
        self._db.commit()

    def delete(self, key):
        self._db.execute('delete from {} where ID = ?'.format(self._table),(key,))
        self._db.commit()

    def RunSQL(self, sql):
        #TODO SQL INJECTION TESTING
        self._db.execute(sql)
        self._db.commit()

    def close(self):
        self._db.close()
        del self._filename

    def __iter__(self):
        cursor = self._db.execute('select * from {} order by DATE DESC'.format(self._table))
        for row in cursor:
            yield dict(row)

#read a csv file into the Database
def CSVToDB(filename):
    global filen
    db = Database(filename = filen,table = 'daily')
    budget = ReadInCSV(filename)
    count = len(budget)-1
    for row in budget:
        row = dict(Date = ToDateStringDB(row[0]), Description=row[1], Debt=row[2], Credit=row[3], Ord=count)
        row = CleanEntry(row)
        row = DollarsToCents(row)
        db.insert(row)
        count -= 1

#print all entries in the daily table
def PrintAll(db):
    for row in db:
        print('{}: {} {} {} {} {}'.format(row['ID'], row['Date'], row['Description'], row['Debt'], row['Credit'], row['Ord']))

if __name__ == "__main__":
    db = Database(filename = filen,table = 'daily')
    db.RunSQL('drop table daily')
    db.RunSQL('create table daily (ID INTEGER PRIMARY KEY NOT NULL, Date text, Description text, Debt int, Credit int, Ord int NOT NULL)')
    CSVToDB(filename)
    PrintAll(db)
