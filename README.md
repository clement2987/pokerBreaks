so much to do, have to create global variables to handle potential changes to the length of required breaks in the future. this should be done by adding a settings.json file and a globals.py file whos job is to read the settings.json and store the values in variables. 

need a python file that can read and update settings.json, this should also trigger globals.py to reload the variables as well as restart the app so the break scadual reflects the changes

have to add class functionto the break sorter to recalculate table breaks if a table goes on break early

add a log to the table class to keep track of when it goes on break and how many breaks it takes

need an async function to keep track of the time and every 15 minutes make sure any tables due for break have gone, else alert the user

after all this will need a gui

while building the gui will build a server and mobile app on swift using websockets to keep the mobile and pc apps in sync
