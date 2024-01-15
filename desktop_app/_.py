# import tkinter as TK
import datetime
# import time

# n = 0

# def main():
#     print("main called")

# def task():
#     print("it has been 30 seconds")

# def check_time():
#     current_time = datetime.datetime.now().time()
#     if current_time.second in [5, 15, 30, 45]:
#         task()
#     main()
#     root.after(1000, check_time)

# def add_text():
#     global n
#     n += 1
#     label.config(text=f"button pressed {n} times")

# root = TK.Tk()
# button = TK.Button(root, text="Press Me", command=add_text)
# button.pack()
# label = TK.Label(root, text="")
# label.pack()

# check_time()
# root.mainloop()

def get_gaming_day_base(date, offset, h=6, m=0):
    """
    takes the date and the desired time and calculates the timestamp 
    (seconds since epoch <01/01/1970 00:00>) if the date. takes as 
    arguments: the date in format "yyyy-mm-dd" and the offset for the
    desired timezone. optional arguments for the time, h=hour and m=minute
    time is 06:00 by default
    """
    specific_date = datetime.datetime.strptime(date, '%Y-%m-%d')

    # Create a new datetime object for 6 AM on the specified date
    six_am_date = specific_date.replace(hour=h, minute=m, second=0)
    timezone = datetime.timezone(datetime.timedelta(hours=offset, minutes=0))
    six_am_date = six_am_date.replace(tzinfo=timezone)

    # Get the time difference in seconds since the epoch (January 1, 1970)
    epoch = datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)
    seconds_since_epoch = (six_am_date - epoch).total_seconds()

    return seconds_since_epoch

class Table():
    def __init__(self, table_number, timestamp):
        self.table_number = table_number
        self.opened = timestamp

    def __str__(self):
        return f"{self.table_number:02d}"


class Break_sorter():
    def __init__(self):
        self.hours = dict()
        self.base = get_gaming_day_base("2023-12-26", 11)
        self.top = self.base + 86400
        n = self.base
        while  n < self.top:
            dt_object = datetime.datetime.fromtimestamp(n)
            hour = dt_object.hour
            minute = dt_object.minute
            self.hours[f"{hour:02d}:{minute:02d}"] = list()
            n+=900
        self.current = n

    def __str__(self):
        output = ""
        for time in self.hours.keys():
            output += f"{time}\n"
            if len(self.hours[time]) > 0:
                output += "    " + "\n    ".join(str(table) for table in self.hours[time]) + "\n"
        return output

    def add_table(self, table):
        n = table.opened + 10800
        while n < self.top:
            dt_object = datetime.datetime.fromtimestamp(n)
            hour = dt_object.hour
            minute = dt_object.minute
            s = f"{hour:02d}:{minute:02d}"
            if s in self.hours:
                self.hours[s].append(table)
            n+=11700

# x  = Break_sorter()
# a = Table(1, get_gaming_day_base("2023-12-26", 11, 12, 0))
# b = Table(2, get_gaming_day_base("2023-12-26", 11, 12, 0))
# c = Table(3, get_gaming_day_base("2023-12-26", 11, 12, 30))
# d = Table(4, get_gaming_day_base("2023-12-26", 11, 13, 0))
# x.add_table(a)
# x.add_table(b)
# x.add_table(c)
# x.add_table(d)
# print(x)

# class Break_sorter():
#     def __init__(self):
#         self.hours = dict()
#         current_time = time.localtime(time.time())
#         current_hour = current_time.tm_hour
#         h = current_hour
#         while True:            
#             self.hours[h] = {
#                 0: list(),
#                 15: list(),
#                 30: list(),
#                 45: list()
#             }
#             h += 1
#             if h > 23:
#                 h = 0
#             if current_hour == h:
#                 break

#     def __str__(self):
#         output = ""
#         for hour in sorted(self.hours.keys()):
#             for quarter in [0, 15, 30, 45]:
#                 output += f"{hour:02d}:{quarter:02d}: "
#                 if self.hours[hour][quarter]:
#                     output += ", ".join(str(table) for table in self.hours[hour][quarter])
#                 output+= "\n"
#         return output
    
#     def add_table(self, table):
#         hour = table.hour
#         minute = table.minute

#         hour += 3
#         if hour > 23:
#             hour -= 24

#         self.hours[hour][minute].append(table)

#         while True:
                     
#             hour += 3
#             if hour > 23:
#                 hour -= 24
#             if hour - table.hour < 3 and hour - table.hour > 0:
#                 break   
            

#             minute += 15
#             if minute == 60:
#                 minute = 0
#                 hour += 1
#             self.hours[hour][minute].append(table)
            


# test = Break_sorter()
# table = Table(16, 12, 0)
# test.add_table(table)
# table = Table(17, 12, 0)
# test.add_table(table)
# table = Table(18, 12, 30)
# test.add_table(table)
# table = Table(19, 13, 45)
# test.add_table(table)
# print(test)



# x = get_gaming_day_base('2023-12-24', 11)
# print(datetime.datetime.fromtimestamp(x))
# print(datetime.datetime.fromtimestamp(int(time.time())))
# print(datetime.datetime(1970, 1, 1))
import json          
def load_dst_dates():
    """
    opens the daylight_savings.json file to gain access to the start and end dates of daylight savings storred there
    """
    with open("daylight_savings.json", 'r') as file:
        return json.load(file)

def get_offset(date, region="melbourne"):
    """
    takes 2 arguments: date in the format "yyyy-mm-dd" and a region (city name) default melbourne then returns 
    the offset from utc to support timezones
    """
    year, month, day = map(int, date.split('-'))
    if region == "melbourne" or region == "sydney":
        daylight_savings_data = load_dst_dates()
        if str(year) in daylight_savings_data['AEST']:
            start_date = daylight_savings_data['AEST'][str(year)]['start']
            end_date = daylight_savings_data['AEST'][str(year)]['end']

            start_month, start_day = map(int, start_date.split('-'))
            end_month, end_day = map(int, end_date.split('-'))

            start_datetime = datetime.datetime(year, start_month, start_day)
            end_datetime = datetime.datetime(year, end_month, end_day)
            current_datetime = datetime.datetime(year, month, day)

            if start_datetime <= current_datetime or current_datetime <= end_datetime:
                return 11
        return 10
    
# print(get_offset("2023-12-29"))
    

# import asyncio

# class RepeatedFunctionCaller:
#     def __init__(self):
#         self.loop = asyncio.get_event_loop()
#         self.task = None
#         self.n = 0

#     async def function_to_call(self):
#         while True:
#             self.n += 1
#             # Replace this with the function you want to call repeatedly
#             # print("This is the function being called every second")
#             await asyncio.sleep(1)

#     def start(self):
#         self.task = self.loop.create_task(self.function_to_call())

#     def stop(self):
#         if self.task:
#             self.task.cancel()
#             self.loop.run_until_complete(self.task)
#             self.task = None

#     def show(self):
#         print(self.n)

# async def main():
#     # Instantiate the RepeatedFunctionCaller
#     caller = RepeatedFunctionCaller()
    
#     # Start calling the function every second asynchronously
#     caller.start()

#     # You can continue to input commands or perform other tasks here
#     while True:
#         user_input = input("Enter a command: ")
#         # Process user input or perform other operations
#         print(f"You entered: {user_input}")

#         if user_input == "t":
#             caller.show()
#         # For example, if the user types "exit", stop the caller and break the loop
#         if user_input.lower() == "exit":
#             caller.stop()
#             break

#     print("Exiting the program.")

# if __name__ == "__main__":
#     asyncio.run(main())
    



# from util import Break_sorter, Break_container, Table
# from helpers import get_timestamp

# def main():
#     date = input("what is todays date? format<YYYY-MM-DD>")
#     location = input("what is the location?")
#     main_break_sorter = Break_sorter(date, location)
#     main_break_sorter.add_hours()
#     while True:
#         command = input("what are we doing? ")
#         if command == "exit":
#             break
#         if command == "print":
#             print(main_break_sorter)
#         if command == "open table":
#             t_number = int(input("table: "))
#             t_game = input("game: ")
#             t_hours = int(input("hour: "))
#             t_min = int(input("minute: "))
#             table = Table(t_number, t_game, get_timestamp(main_break_sorter.date, "melbourne", t_hours, t_min))
#             main_break_sorter.add_table(table)

# main()
def listy(time):
    hour, minute = map(int, time.split(":"))
    if hour > 5:
        hour -= 6
    else:
        hour += 18
    return (hour*4)+(minute//15)

times = []
minutes = ['00','15','30','45']
for i in range(6, 24):
    for minute in minutes:
        times.append(f"{i:02d}:{minute}")
for i in range(6):
    for minute in minutes:
        times.append(f"{i:02d}:{minute}")

for t in times:
    print(listy(t))

