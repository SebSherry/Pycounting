#--------------------------------------------------------------------#
#Pycounting V1.0
#Created, Written, Developed and Designed by Sebastian Sherry April 2016
#This program is licensed under the GNU General Public License v3.0
#--------------------------------------------------------------------#
#imports
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import *

#Import rest of the program
from  Budget_calc import *
from util import *

#Fonts
FONT_LARGE = ('Verdana', 24)
FONT_NORM = ('Verdana', 12)

#--------------------------------------------------------------------#
class Pycounting(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        tk.Tk.wm_title(self, "Pycounting")

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand = True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        #menu
        #menubar = tk.Menu(container)
        #filemenu = tk.Menu(menubar, tearoff=0)
        #filemenu.add_command(label="Text", command="command")
        #filemenu.add_separator()
        #tk.Tk.config(self, menu=menubar)

        #dictionary to hold all windows
        self.frames = {}

        #add pages to frames
        for F in (DailyBudgetPage, WeeklySummary):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row = 0, column = 0, sticky="nsew")

        #show startpage
        self.show_frame(DailyBudgetPage)

    #shows the desired frame
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

#Daily Budget page
class DailyBudgetPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        #display = Text(window, width = 20, height = 18, wrap = WORD, font = ('Verdana', 12), borderwidth = 2, relief = 'groove')
        #setup tree to hold entries
        self.tree = ttk.Treeview(self, columns=('date','description', 'debt', 'credit', 'balance'))
        self.tree.bind("<Double-1>", self.ModifyEntry)
        self.tree.column('date', width=64, anchor='center')
        self.tree.column('description', minwidth=120, anchor='center')
        self.tree.column('debt',width=80,  anchor='center')
        self.tree.column('credit',width=80,  anchor='center')
        self.tree.column('balance',width=80,  anchor='center')
        self.tree.heading('date', text='Date')
        self.tree.heading('description', text='Item')
        self.tree.heading('debt', text='Debt')
        self.tree.heading('credit', text='Credit')
        self.tree.heading('balance', text='Balance')
        self.tree['show'] = ('headings')

        heading = ttk.Label(self, text = 'Daily Budget', font = FONT_LARGE, justify = 'center')
        #count = Label(window, text = '1/1', justify = CENTER)
        btnFrame = ttk.Frame(self)
        addbtn = ttk.Button(btnFrame, text = 'Add', command=self.addDailyEntry)
        quitbtn = ttk.Button(btnFrame, text = 'Quit', command=quit)
        outbtn = ttk.Button(btnFrame, text = 'ToCSV', command=self.ToCSV)
        #place widgets
        heading.grid(row = 1, column = 1, columnspan = 3,pady=10)
        self.tree.grid(row = 2, column = 1, columnspan = 3, padx=420)
        btnFrame.grid(row=3, column=2,pady=3)
        outbtn.grid(row = 1, column = 1, padx=1)
        addbtn.grid(row = 1, column = 2, padx=1)
        quitbtn.grid(row = 1, column = 3, padx=1)

        #intizlize tree
        self.DisplayAccount()

    #displays the current account
    def DisplayAccount(self):
        budget = GetDailyBudget()
        if budget != []:
            balances = GenBalance()
            #clear treeview if already populated
            self.ClearDisplay()
            #loop through entries
            for entry in budget:
                entry = FormatEntry(entry)
                amt = 0
                for bal in balances:
                    if bal['ID'] == entry[4]:
                        amt = "$"+str(bal['BAL'])
                        break
                disEntry = [entry[0],entry[1],entry[2],entry[3],amt,entry[4],entry[5]]
                self.tree.insert('','end', values=(disEntry))

    #deletes all entries in the treeview
    def ClearDisplay(self):
        for row in self.tree.get_children():
            self.tree.delete(row)


    #handles adding an entry to the list
    #Add Entry to budget
    def addDailyEntry(self, entry=[]):
        add = tk.Tk()
        add.wm_title("Add Entry")
        add.geometry("570x100")

        #exit return function
        def grab():
            tempEntry = [entDate.get(), entDsc.get(), "$-", "$-","0","0"]
            if self.entryType.get() == "Debt":
                tempEntry[2] = entAmt.get()
            elif self.entryType.get() == "Credit":
                tempEntry[3] = entAmt.get()
            tempEntry = ToDict(tempEntry)
            if entry != []:
                tempEntry['ID'] = entry['ID']
                tempEntry['Ord'] = entry['Ord']
                #done = False
                done = EditEntry(CleanEntry(entry),CleanEntry(tempEntry))
            else:
                #set order
                tempEntry['Ord'] = len(self.tree.get_children())
                #add new entry
                AddEntry(tempEntry)
            #update Display
            self.DisplayAccount()
            #close popup
            add.destroy()

        #variables
        self.date = tk.StringVar(add)
        self.desc = tk.StringVar(add)
        self.amount = tk.StringVar(add)
        self.entryType = tk.StringVar(add)
        defaultType = "Debt"
        if (entry != []):
            self.date.set(entry['Date'])
            self.desc.set(entry['Description'])
            if entry['Credit'] == "$0.0":
                self.amount.set(entry['Debt'])
                self.entryType.set("Debt")
            else:
                self.amount.set(entry['Credit'])
                self.entryType.set("Credit")
                defaultType = "Credit"
        else:
            #set default date and entryType
            dateStr = GetCurrentDateFormatted(True);
            self.date.set(dateStr)
            self.amount.set("$")
            self.entryType.set("Debt")

        #labels
        lblDate = ttk.Label(add, text = 'Date', font = FONT_NORM, justify = 'center')
        lblDsc = ttk.Label(add, text = 'Description', font = FONT_NORM, justify = 'center')
        lblAmt = ttk.Label(add, text = 'Amount', font = FONT_NORM, justify = 'center')

        #Entries, optionmenu, and buttons
        entDate = ttk.Entry(add, textvariable=self.date,justify="center")
        entDsc = ttk.Entry(add, textvariable=self.desc)
        entDsc.focus_set()
        entAmt = ttk.Entry(add, textvariable=self.amount)
        cmbTrans = ttk.OptionMenu(add, self.entryType, defaultType, "Debt", "Credit")
        btnSub = ttk.Button(add, text = 'Submit', command=grab)
        btnQuit = ttk.Button(add, text = 'Quit', command=add.destroy)

        #grid layout
        lblDate.grid(row=1,column=1)
        lblDsc.grid(row=1,column=2)
        lblAmt.grid(row=1,column=3)
        entDate.grid(row=2,column=1)
        entDsc.grid(row=2,column=2)
        entAmt.grid(row=2,column=3)
        cmbTrans.grid(row=2,column=4)
        btnSub.grid(row=3,column=1,columnspan=2)
        btnQuit.grid(row=3,column=3,columnspan=2)

        #main loop
        add.mainloop

    def ModifyEntry(self, event):
        item = self.tree.selection()[0]
        entry = ToDict(self.tree.item(item,"values"), False)
        #entry = self.tree.item(item,"values")

        opt = tk.Tk()
        opt.wm_title("")
        #opt.geometry("500x350")

        btnMod = ttk.Button(opt, text = 'Edit',command=lambda: Modify(entry))
        btnDel = ttk.Button(opt, text = 'Delete',command=lambda: Delete(entry))
        btnUp = ttk.Button(opt, text = 'Move Up',command=lambda: MoveUp(entry))
        btnDn = ttk.Button(opt, text = 'Move Down',command=lambda: MoveDown(entry))
        btnCnl = ttk.Button(opt, text = 'Cancel', command=opt.destroy)

        btnMod.pack(fill='x')
        btnDel.pack(fill='x')
        btnUp.pack(fill='x')
        btnDn.pack(fill='x')
        btnCnl.pack(fill='x')

        opt.mainloop

        def Modify(entry):
            opt.destroy()
            self.addDailyEntry(entry)

        def Delete(entry):
            result = messagebox.askyesno(message='Are you sure you want to delete this entry?',icon='question',title='Delete?')
            if result == True:
                wait = False
                wait = RemoveEntry(entry)
                #update Display
                self.DisplayAccount()
                #close popup
                opt.destroy()

        def MoveUp(entry):
            if int(entry['Ord']) == (len(self.tree.get_children())-1):
                messagebox.showinfo(message='Cannot move entry. Already at the top')
            else:
                second = self.tree.next(item)
                second = ToDict(self.tree.item(second,"values"), False)
                if entry['Date'] != second['Date']:
                    messagebox.showinfo(message='Cannot move entry. Dates would longer be in order')
                else:
                    wait = False
                    wait = swapEntries(CleanEntry(entry),CleanEntry(second))
                    #update Display
                    self.DisplayAccount()
                    #close popup
                    opt.destroy()

        def MoveDown(entry):
            if int(entry['Ord']) == 0:
                messagebox.showinfo(message='Cannot move entry. Already at the bottom')
            else:
                second = self.tree.next(item)
                second = ToDict(self.tree.item(second,"values"), False)
                if entry['Date'] != second['Date']:
                    messagebox.showinfo(message='Cannot move entry. Dates would longer be in order')
                else:
                    wait = False
                    wait = swapEntries(CleanEntry(entry),CleanEntry(second))
                    #update Display
                    self.DisplayAccount()
                    #close popup
                    opt.destroy()

    def ToCSV(self):
        messagebox.showinfo(message='This feature is currently disabled')

#Week by week budget summary
class WeeklySummary(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        heading = ttk.Label(self, text = 'Account', font = FONT_LARGE, justify = 'center')
        nextbtn = ttk.Button(self, text = 'Display', command=lambda: controller.show_frame(DailyBudgetPage))

        heading.pack()
        nextbtn.pack()

#define app and settings
app = Pycounting()
#app.geometry("1280x720")
#launch app
app.mainloop()
