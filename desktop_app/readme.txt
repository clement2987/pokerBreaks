If daylight savings time is not automatically being applied then the most likely cause is the dates have not been added to the JSON file "daylight_savings.json"
and the file needs to be updated, this can either be done by TODO or by manually opening the json file and adding the dates for the years not currently supported
if this is done manually make sure that the person preforming the task is familiar with json format as any mistakes could cause unpredictable behavour

# TODO
write function to load state
turn lights green when table goes on break
network with phone app
add settings and test if when settings are changed everything still works
make sure daylight savings are being handled
write function to generate report
make sure state.json is being updated with every change
find a way to create a file path to save the reports, the file path should be saved in settings.json and should be chosen by the user using the file explorer
when opening a table we should check if the table has been open previously and reopen it instead
allow log to have a table closed then imediatly reopened
add to this file as I remember things

BUGS:
lable in timeframs move to the cener of the widget when table is closed
