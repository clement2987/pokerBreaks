import datetime

import globals
from helpers import get_gaming_day_base, hour_change, get_timestamp

class Table(): #TODO add logic to handle a table being reopened
    def __init__(self, table_number, game, timestamp):
        self.table_number = table_number
        self.game = game
        self.breaks = list()
        self.opened = timestamp
        self.closed = None
        # a variable starting point to facilitate the break sorters functionality as a tables breaks may not always be based on the time a table opened
        self.start_point = timestamp

    def __str__(self):
        return f"{self.table_number:02d}"
    
    def send_on_break(self, timestamp):
        self.breaks.append(timestamp)


class Break_sorter():
    def __init__(self, date=0, location="melbourne"):
        self.hours = dict()
        self.base = get_gaming_day_base("2023-12-26", location)
        self.top = self.base + globals.DAY
        dt_object = datetime.datetime.fromtimestamp(self.top)
        formatted_date = dt_object.strftime("%Y-%m-%d")
        self.change = hour_change(formatted_date, location)        

    def __str__(self):
        output = ""
        for time in self.hours.keys():
            output += f"{time[:5]}\n"
            if len(self.hours[time]) > 0:
                output += "    " + "\n    ".join(str(table) for table in self.hours[time]) + "\n"
        return output
    
    def add_hours(self):
        n = self.base
        while  n < self.top:
            dt_object = datetime.datetime.fromtimestamp(n)
            hour = dt_object.hour
            minute = dt_object.minute
            self.hours[f"{hour:02d}:{minute:02d}-{n}"] = list()
            n+=globals.BREAK_TIME
        self.current = n

    def add_table(self, table):
        n = table.start_point + globals.MAX_PLAY_TIME
        while n < self.top:
            dt_object = datetime.datetime.fromtimestamp(n)
            hour = dt_object.hour
            minute = dt_object.minute
            s = f"{hour:02d}:{minute:02d}-{n}"
            if s in self.hours:
                self.hours[s].append(table)
            n+=globals.TOTAL_TIME

    def remove_table_from_future_list(self, table, timestamp):
        for time in self.hours.keys():
            if timestamp > float(time[6:]):
                continue
            if table in self.hours[time]:
                self.hours[time].remove(table)

    def recalculate_break(self, table):
        returned_from_break = max(table.breaks) + globals.BREAK_TIME
        table.start_point = returned_from_break
        self.remove_table_from_future_list(table, returned_from_break)
        self.add_table(table)


class DLS_end_break_sorter(Break_sorter):
    def add_hours(self):
        n = self.base
        self.top += globals.HOUR
        self.add_hour = n + globals.TIME_TO_THREE_AM
        after_2 = False
        while  n < self.top:
            if n >= self.add_hour and after_2 == False:
                after_2 = True
            dt_object = datetime.datetime.fromtimestamp(n)
            hour = dt_object.hour
            minute = dt_object.minute
            if after_2 == False:
                self.hours[f"{hour:02d}:{minute:02d}-{n}"] = list()
            elif after_2 == True and hour == 3:
                self.hours[f"+{hour-1:02d}:{minute:02d}-{n}"] = list()
            else:
                self.hours[f"{hour-1:02d}:{minute:02d}-{n}"] = list()
            n+=globals.BREAK_TIME
        self.current = n

    def add_table(self, table):
        n = table.start_point + globals.MAX_PLAY_TIME
        after_2 = False
        while n < self.top:
            if n >= self.add_hour and after_2 == False:
                after_2 = True
            dt_object = datetime.datetime.fromtimestamp(n)
            hour = dt_object.hour
            minute = dt_object.minute
            if after_2 == False:
                s = f"{hour:02d}:{minute:02d}-{n}"
            elif after_2 == True and hour == 3:
                s = f"+{hour-1:02d}:{minute:02d}-{n}"
            else:
                s = f"{hour-1:02d}:{minute:02d}-{n}"
            if s in self.hours:
                self.hours[s].append(table)
            n+=globals.TOTAL_TIME

class DLS_start_break_sorter(Break_sorter):
    def hour_difference(self, timestamp):
        two_am = self.base + globals.TIME_TO_TWO_AM
        if timestamp >= two_am:
            return timestamp + globals.HOUR
        return timestamp

    def add_hours(self):
        n = self.base
        while  n < self.top:
            dt_object = datetime.datetime.fromtimestamp(self.hour_difference(n))
            hour = dt_object.hour
            minute = dt_object.minute
            self.hours[f"{hour:02d}:{minute:02d}-{n}"] = list()
            n+=globals.BREAK_TIME
        self.current = n

    def add_table(self, table):
        n = table.start_point + globals.MAX_PLAY_TIME
        while n < self.top:
            dt_object = datetime.datetime.fromtimestamp(self.hour_difference(n))
            hour = dt_object.hour
            minute = dt_object.minute
            s = f"{hour:02d}:{minute:02d}-{n}"
            if s in self.hours:
                self.hours[s].append(table)
            n+=globals.TOTAL_TIME

if __name__=="__main__":
    x = Break_sorter()
    x.add_hours()
    a = Table(1, "2/5 nlh", get_timestamp("2023-12-26", "melbourne", 12, 0))
    b = Table(2, "2/5 nlh", get_timestamp("2023-12-26", "melbourne", 12, 0))
    c = Table(3, "2/5 nlh", get_timestamp("2023-12-26", "melbourne", 12, 30))
    d = Table(4, "2/5 nlh", get_timestamp("2023-12-02", "melbourne", 14, 30))
    x.add_table(a)
    x.add_table(b)
    x.add_table(c)
    x.add_table(d)
    print(x)
    a.send_on_break(get_timestamp("2023-12-26", "melbourne", 15, 0))
    a.send_on_break(get_timestamp("2023-12-26", "melbourne", 18, 15))
    a.send_on_break(get_timestamp("2023-12-26", "melbourne", 20, 0))
    x.recalculate_break(a)
    print(x)