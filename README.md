# Pycounting
An accounting program written in python 3

Created, Written, Developed and Designed by Sebastian Sherry April 2016
This program is licensed under the GNU General Public License v3.0

# How to Run
Just run the pycounting.py file. Note that Tkinter is required to run

NOTE: It is recommend to run from the directory pycounting.py is in to prevent
issues with finding the database file. The program WILL run regardless of where
you run it, but your data will obviously not carry over if opened from a different
location. This is an issue I hope to resolve in the future.

# How to use
The interface is designed to be as self explanatory as possible, but here's some
clarifying notes:

- To add an entry, click the add bottom below the table
- Entry the details of the entry into the correct fields. Note the date defaults to current date
- Double clicking on an entry will bring up an options menu
- Edit will bring up the same interface as add entry
- Remove will delete the entry from the database
- Move up and Down will adjust the position of the entry on the table. Note that
an entry cannot be moved to a position where another entry of a different date separates it (Currently not working)
from entries of the same date.
- ToCSV will (eventually) output the contents of a table to a CSV file
- The menu bar can be used to view both the Daily Budget and Weekly Summary breakdowns

# Known Bugs
- When there is only one entry on the table, attempting to remove it will fail.
the program will still operate. It is recommend that the user edits the entry in
this case rather than deleting and making a new entry.
- The Debt/Credit drop down may not appear in the add/modify screen on OSx.

If you find a bug that is not recorded here, please let me know.
