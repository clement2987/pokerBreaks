import datetime
import requests

import globals
from helpers import get_gaming_day_base, hour_change, get_timestamp

class Request_handler():
    def __init__(self):
        self.domain = globals.DOMAIN
        self.key = globals.KEY

    def login(self):
        ...

    def send_breaks(self, breaks):
        url = self.domain + "/breaks"
        message = {
            "key": self.key,
            "break_scadual": breaks
        }
        responce = requests.post(url, json=message)

        print(responce)

class Table():
    def __init__(self, table_number, game, timestamp):
        self.table_number = table_number
        self.state = "open"
        self.game = game
        self.breaks = list()
        self.log = dict()
        self.log[timestamp] = f"opened as {game}"
        self.opened = timestamp
        self.closed = None
        self.start_point = timestamp

    def __str__(self):
        return f"{self.table_number:02d}"
    
    def send_on_break(self, timestamp):
        self.breaks.append(timestamp)
        if timestamp in self.log:
            if self.log[timestamp] != "sent on break":
                timestamp+=1
        self.log[timestamp] = "sent on break"
    
    def close_table(self, timestamp):
        self.state = "closed"
        if timestamp in self.log:
            timestamp+=1
        self.log[timestamp] = "closed"
    
    def reopen_table(self, timestamp, game):
        self.state = "open"        
        self.start_point = timestamp
        self.game = game
        self.breaks.append(timestamp)
        if timestamp in self.log:
            timestamp+=1
        self.log[timestamp] = f"opened as {game}"

class Break_container():
    def __init__(self, table, timestamp):
        self.table = table
        self.scadualed_break = timestamp
        self.sent = False
        self.anounced = False
        self.chip_count = False
        self.table_rolled = False
        self.sign = False
        self.called_back = False

    def __str__(self):
        return str(self.table)
    
    def send_on_scadualed_break(self):
        self.table.send_on_break(self.scadualed_break)
        self.sent = True
    
    def send_on_unscadualed_break(self):
        #TODO add logic to find timestamp to the nearst break window and send on break at that time Should add a variable to settings that gets updated every window
        self.sent = True
    
    def anounce(self):
        self.anounced = True

    def add_chip_count(self):
        self.chip_count = True
    
    def role_table(self):
        self.table_rolled = True

    def update_sign(self):
        self.sign = True

    def call_back(self):
        self.called_back = True


class Break_sorter():
    def __init__(self, date="2023-12-26", location="melbourne"):
        self.hours = dict()
        self.location = location
        self.date = date
        self.base = get_gaming_day_base(date, location)
        self.top = self.base + globals.DAY
        dt_object = datetime.datetime.fromtimestamp(self.top)
        formatted_date = dt_object.strftime("%Y-%m-%d")
        self.change = hour_change(formatted_date, location)
        globals.TODAY = date     

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
        if table.state == "closed":
            return
        n = table.start_point + globals.MAX_PLAY_TIME
        while n < self.top:
            dt_object = datetime.datetime.fromtimestamp(n)
            hour = dt_object.hour
            minute = dt_object.minute
            s = f"{hour:02d}:{minute:02d}-{n}"
            if s in self.hours:
                container = Break_container(table, n)
                self.hours[s].append(container)
            n+=globals.TOTAL_TIME

    def remove_table_from_future_list(self, table, timestamp):        
        for time in self.hours.keys():
            if timestamp > float(time[6:]):
                continue
            to_be_removed = list()
            for container in self.hours[time]:
                if container.table == table:
                    to_be_removed.append(container)
            for container in to_be_removed:
                self.hours[time].remove(container)

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
        if table.state == "closed":
            return
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
                container = Break_container(table, n)
                self.hours[s].append(container)
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
        if table.state == "closed":
            return
        n = table.start_point + globals.MAX_PLAY_TIME
        while n < self.top:
            dt_object = datetime.datetime.fromtimestamp(self.hour_difference(n))
            hour = dt_object.hour
            minute = dt_object.minute
            s = f"{hour:02d}:{minute:02d}-{n}"
            if s in self.hours:
                container = Break_container(table, n)
                self.hours[s].append(container)
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