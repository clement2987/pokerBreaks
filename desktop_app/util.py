import datetime

from helpers import get_gaming_day_base, hour_change, get_timestamp

class Table():
    def __init__(self, table_number, game, timestamp):
        self.table_number = table_number
        self.game = game
        self.opened = timestamp
        self.closed = None

    def __str__(self):
        return f"{self.table_number:02d}"


class Break_sorter():
    def __init__(self, date=0, location="melbourne"):
        self.hours = dict()
        self.base = get_gaming_day_base("2023-12-26", location)
        self.top = self.base + 86400
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
            n+=900
        self.current = n

    def add_table(self, table):
        n = table.opened + 10800
        while n < self.top:
            dt_object = datetime.datetime.fromtimestamp(n)
            hour = dt_object.hour
            minute = dt_object.minute
            s = f"{hour:02d}:{minute:02d}-{n}"
            if s in self.hours:
                self.hours[s].append(table)
            n+=11700

class DLS_end_break_sorter(Break_sorter):
    def add_hours(self):
        n = self.base
        self.top += 3600
        self.add_hour = n + 75600
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
            n+=900
        self.current = n

    def add_table(self, table):
        n = table.opened + 10800
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
            n+=11700

class DLS_start_break_sorter(Break_sorter):
    def hour_difference(self, timestamp):
        two_am = self.base + 72000
        if timestamp >= two_am:
            return timestamp + 3600
        return timestamp

    def add_hours(self):
        n = self.base
        while  n < self.top:
            dt_object = datetime.datetime.fromtimestamp(self.hour_difference(n))
            hour = dt_object.hour
            minute = dt_object.minute
            self.hours[f"{hour:02d}:{minute:02d}-{n}"] = list()
            n+=900
        self.current = n

    def add_table(self, table):
        n = table.opened + 10800
        while n < self.top:
            dt_object = datetime.datetime.fromtimestamp(self.hour_difference(n))
            hour = dt_object.hour
            minute = dt_object.minute
            s = f"{hour:02d}:{minute:02d}-{n}"
            if s in self.hours:
                self.hours[s].append(table)
            n+=11700

if __name__=="__main__":
    x = DLS_start_break_sorter()
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