import customtkinter
import tkinter
from tkinter import messagebox
from time import time
import datetime
import json

customtkinter.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

from util import Break_sorter, Table, Break_container
from helpers import get_formatted_date, check_valid_date, get_time_nearest_15, get_timestamp, get_date_time_from_timestamp, get_time_from_timestamp
import globals


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        #app tools
        self.break_sorter = None
        self.tables = list()
        self.closed_table_objects = list()

        self.closed_tables = globals.TABLES
        self.open_tables = list()

        # configure window
        self.title("Poker table break sorter")
        self.geometry(f"{1100}x{640}")

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)

        # create sidebar frame with widgets
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, height=560, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="Main Functions", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        self.sidebar_button_1 = customtkinter.CTkButton(self.sidebar_frame, text="Start break sorter", command=self.break_sorter_window)
        self.sidebar_button_1.grid(row=1, column=0, padx=20, pady=10)
        self.sidebar_button_2 = customtkinter.CTkButton(self.sidebar_frame, text="Open Table", command=self.open_table)
        self.sidebar_button_2.grid(row=2, column=0, padx=20, pady=10)
        self.sidebar_button_3 = customtkinter.CTkButton(self.sidebar_frame, text="Save state", command=self.save_state)
        self.sidebar_button_3.grid(row=4, column=0, padx=20, pady=10)
        self.sidebar_button_4 = customtkinter.CTkButton(self.sidebar_frame, text="Somthing else", command=None)
        self.sidebar_button_4.grid(row=5, column=0, padx=20, pady=10)

        #create tabs
        self.tabs = customtkinter.CTkTabview(self, width=900, height=560)
        self.tabs.grid(row=0, column=1)
        self.tabs.add("dashboard")
        self.tabs.add("tables")
        self.tabs.add("settings")
        self.tabs.add("something else")

        #dashboard
        self.tabs.tab("dashboard").grid_columnconfigure(0, minsize=590)
        self.tabs.tab("dashboard").grid_columnconfigure(1, minsize=300)
        self.tabs.tab("dashboard").grid_rowconfigure(0, minsize=400)
        self.tabs.tab("dashboard").grid_rowconfigure(1, minsize=150)

        self.time_frames = customtkinter.CTkScrollableFrame(self.tabs.tab("dashboard"), label_text="Table Break List", height=380)
        self.time_frames.grid(row=0, column=1)

        self.dashboard_main = customtkinter.CTkFrame(self.tabs.tab("dashboard"), width=580, height=400)
        self.dashboard_main.grid(row=0, column=0, sticky="nsew")
        self.date_label = customtkinter.CTkLabel(self.dashboard_main, text="", font=("Open Sans", 30))
        self.date_label.grid(row=0, column=0)
        self.time = customtkinter.CTkLabel(self.dashboard_main, text="", font=("Open Sans", 30))
        # self.time.grid_columnconfigure(0, minsize=500)
        self.time.grid(row=1, column=0)
        self.main_rows = [customtkinter.CTkLabel(self.dashboard_main, text="", font=("Open Sans", 16), anchor="w", justify="left") for _ in range(8)]

        self.officers = customtkinter.CTkFrame(self.tabs.tab("dashboard"), height=110, width=300)
        self.officers.grid(row=1, column=1)

        self.alerts = customtkinter.CTkFrame(self.tabs.tab("dashboard"), width=580, height=140)
        self.alerts.grid(row=1, column=0)
        self.alerts.pack_propagate(False)
        self.alert = customtkinter.CTkLabel(self.alerts, text="No alerts, 200 okay", font=("Open Sans", 20), width=400, height=20)
        self.alert.pack(pady=10, expand=0)

        #tables
        self.tabs.tab("tables").grid_columnconfigure(0, minsize=590)
        self.tabs.tab("tables").grid_columnconfigure(1, minsize=300)
        self.tabs.tab("tables").grid_rowconfigure(0, minsize=400)
        self.tabs.tab("tables").grid_rowconfigure(1, minsize=150)

        self.table_frames = customtkinter.CTkScrollableFrame(self.tabs.tab("tables"), label_text="open table List", height=380)
        self.table_frames.grid(row=0, column=1)

        self.focused_table_frame = customtkinter.CTkFrame(self.tabs.tab("tables"), width=580, height=400)
        self.focused_table_frame.grid(row=0, column=0)


    def refresh_app(self):
        self.populate_timeframes()
        self.list_tables()
        self.populate_main_display(time())

    def time_check(self):
        current_time = datetime.datetime.now().time()
        self.time.configure(text=f"{current_time.hour:02d}:{current_time.minute:02d}:{current_time.second:02d}")
        current_timestamp = time()
        alert = ""
        for table in self.tables:
            check = list(table.log.keys())
            if table.state == "open" and current_timestamp-max(check)>globals.MAX_PLAY_TIME:
                alert += f" {table.table_number:02d} "
        if current_timestamp - self.break_sorter.base > globals.DAY:
            alert += "\nGaming does not match the current day"
        if alert == "":
            self.alert.configure(text="No alerts, 200 okay")
        elif alert[0] == " ":
            self.alert.configure(text="The following tables are late for break"+alert)
        else:
            self.alert.configure(text=alert)
        
        if current_time.minute in [0, 15, 30, 45]:
            self.populate_main_display(current_timestamp)
        

        self.after(1000, self.time_check)

    def break_sorter_window(self):
        window = customtkinter.CTkToplevel(self)
        window.title("start break sorter")
        window.geometry("700x450")
        window.grab_set()

        def cancel():
            window.destroy()

        def start_break_sorter():
            s = entry.get()
            try:
                day, month, year = map(int, s.split('-'))
                date = f"{year}-{month:02d}-{day:02d}"
                if check_valid_date(date) == False:
                    raise ValueError
                self.break_sorter = Break_sorter(date, location=globals.LOCATION)
                self.break_sorter.add_hours()
                if len(self.tables) > 0:
                    for table in self.tables:
                        self.break_sorter.add_table(table)
                self.refresh_app()
                self.date_label.configure(text=s)
                self.populate_main_display(time())
                self.time_check()
                cancel()
            except ValueError:
                error.configure(text="invalid date format")
            
                

        if self.break_sorter:
            warning = customtkinter.CTkLabel(window, text="WARNING: changing the break sorter while app is running could lead to loss of data and future compliance issues")
            warning.pack(pady=20)

        label_1 = customtkinter.CTkLabel(window, text="date: dd-mm-yyyy")
        label_1.pack(pady=20)
        entry = customtkinter.CTkEntry(window)
        entry.pack(pady=10)
        entry.insert(0, get_formatted_date())

        start_button = customtkinter.CTkButton(window, text="start app", command=start_break_sorter)
        start_button.pack(pady=40)
        cancel_button = customtkinter.CTkButton(window, text="cancel", command=cancel)
        cancel_button.pack()

        error = customtkinter.CTkLabel(window, text="")
        error.pack()

    def open_table(self):
        window = customtkinter.CTkToplevel(self)
        window.title("Open Table")
        window.geometry("700x450")
        window.grab_set()

        def cancel():
            window.destroy()

        def add_table():
            tn = table_number.get()
            if tn not in self.closed_tables:
                error.configure(text="Invalid table selection")
                return
            g = game.get()
            s = gdate.get()
            t = time.get()
            try:
                n = int(tn)
                day, month, year = map(int, s.split('-'))
                hour, minute = map(int, t.split(':'))
                gaming_date_offset = 0
                if hour < 6:
                    gaming_date_offset = globals.DAY
                date = f"{year}-{month:02d}-{day:02d}"
                if check_valid_date(date) == False:
                    raise ValueError
                timestamp = get_timestamp(date, globals.LOCATION, h=hour, m=minute)
                table = Table(n, g, timestamp + gaming_date_offset)
                if tn in self.open_tables: 
                    error.configure(test="table is already open")
                if self.break_sorter:
                    self.break_sorter.add_table(table)
                self.tables.append(table)
                self.closed_tables.remove(tn)
                self.open_tables.append(tn)
                table_number.configure(values=self.closed_tables)
                if len(self.closed_tables) > 0:
                    table_number.set(self.closed_tables[0])
                self.refresh_app()
            except ValueError:
                pass
                error.configure(text="invalid date or time format, date must be <DD-MM-YYYY> and time must be <HH:MM>")

        label_1 = customtkinter.CTkLabel(window, text="Table number")
        label_1.pack(pady=5)
        table_number = customtkinter.CTkComboBox(window, values=self.closed_tables)
        table_number.pack(pady=5)

        label_2 = customtkinter.CTkLabel(window, text="Game type")
        label_2.pack(pady=5)
        game = customtkinter.CTkComboBox(window, values=globals.GAMES)
        game.pack(pady=5)

        label_3 = customtkinter.CTkLabel(window, text="Date opened")
        label_3.pack(pady=5)
        gdate = customtkinter.CTkEntry(window)
        gdate.pack(pady=5)
        gdate.insert(0, get_formatted_date())

        label_4 = customtkinter.CTkLabel(window, text="Time opened")
        label_4.pack(pady=5)
        time = customtkinter.CTkEntry(window)
        time.pack(pady=5)
        time.insert(0, get_time_nearest_15())

        start_button = customtkinter.CTkButton(window, text="Add table", command=add_table)
        start_button.pack(pady=5)

        cancel_button = customtkinter.CTkButton(window, text="Close", command=cancel)
        cancel_button.pack(pady=5)

        error = customtkinter.CTkLabel(window, text="")
        error.pack()

    def send_on_break(self, timestamp=None, break_container=None, table=None):
        if break_container != None:
            break_container.send_on_scadualed_break()
            return
        elif timestamp != None and table != None:
            table.send_on_break(timestamp)
            self.break_sorter.recalculate_break(table)
            self.refresh_app()
            self.focus_table(table.table_number)
            return
        elif table != None:
            while True:
                dialog = customtkinter.CTkInputDialog(text="Type in the time of the break <HH:MM>", title="Break time")
                response = dialog.get_input()
                if response == None:
                    return
                try:
                    ts = get_time_nearest_15(timestamp=True, dtime=f"{globals.TODAY}{response}")
                    table.send_on_break(ts)
                    self.break_sorter.recalculate_break(table)
                    self.refresh_app()
                    self.focus_table(table.table_number)
                    return
                except ValueError:
                    continue
            
        

        
    def refresh_timeframes(self):
        if self.time_frames:
            self.time_frames.destroy()
        self.time_frames = customtkinter.CTkScrollableFrame(self.tabs.tab("dashboard"), label_text="Table Break List", height=380)
        self.time_frames.grid(row=0, column=1)

    def populate_main_display(self, timestamp):
        keys = list(self.break_sorter.hours.keys())
        key_location = 0
        #Find the first location of the break sorter we are interested in displaying
        for key in keys:
            _, t = key.split('-')
            t = float(t)
            if t > timestamp:
                break
            key_location += 1

        for i in range(2, 10):
            index = i-2
            try:
                s = f"{keys[key_location][:5]}:"
                for table in self.break_sorter.hours[keys[key_location]]:
                    s += f"    {table.table.table_number:02d}"
                self.main_rows[index].configure(text=s)
                self.main_rows[index].grid(row=i, column=0, sticky="w")
                key_location += 1
            except:
                self.main_rows[index].configure(text="")
                self.main_rows[index].grid(row=i, column=0)
        
    def populate_timeframes(self):
        self.refresh_timeframes()
        if self.break_sorter == None:
            return
        for hour in self.break_sorter.hours.keys():
            time_frame = customtkinter.CTkFrame(self.time_frames)
            time_frame.grid_columnconfigure((0, 1, 2, 3, 4), minsize=40)
            
            customtkinter.CTkLabel(time_frame, text=f"{hour[:5]}:", justify="left", font=("Open Sans", 24)).grid(row=0, column=0)
            if len(self.break_sorter.hours[hour]) > 0:
                n = 1
                for table in self.break_sorter.hours[hour]:
                    time_frame.grid_columnconfigure((0, 1, 2, 3, 4), minsize=15)
                    rb = customtkinter.CTkRadioButton(time_frame, text="", state="disabled", height=10, width=10, border_width_unchecked=2)
                    
                    rb.grid(row=n, column=0)
                    if table.sent:
                        rb.configure(border_color="green")
                    customtkinter.CTkLabel(time_frame, text=f"table {table}", font=("Open Sans", 16)).grid(row=n, column=1)
                    customtkinter.CTkButton(time_frame, text="Break", command=lambda t=table: self.send_on_break(break_container=t), width=10).grid(row=n, column=3)
                    time_frame.grid_rowconfigure(n, pad=10)
                    n+=1                    

            time_frame.pack(pady=5)

    def refresh_table_list(self):
        if self.table_frames:
            self.table_frames.destroy()
        self.table_frames = customtkinter.CTkScrollableFrame(self.tabs.tab("tables"), label_text="open table List", height=380)
        self.table_frames.grid(row=0, column=1)

    def send_table_on_unscadualed_break(self, date, time):
        ...

    def close_table(self, table, timestamp):
        n = f"{table.table_number:02d}"
        table.close_table(timestamp)
        self.open_tables.remove(n)
        self.closed_tables.append(n)
        if self.break_sorter:
            self.break_sorter.remove_table_from_future_list(table, timestamp)
        self.refresh_app()
        self.focus_table(table.table_number)

    def remove_table_completly(self, table):
        responce = messagebox.askquestion("warning", "Are you sure you want to remove the table and delete the log?")
        if responce == "no":
            return
        self.tables.remove(table)
        n = f"{table.table_number:02d}"
        self.open_tables.remove(n)
        self.closed_tables.append(n)
        if self.break_sorter:
            self.break_sorter.remove_table_from_future_list(table, time())
        self.refresh_app()
        self.focus_table(table.table_number)

    def remove_log_item(self, table):
        window = customtkinter.CTkToplevel(self)
        window.title("Remove log item")
        window.geometry("700x450")
        window.grab_set()

        def cancel():
            window.destroy()
        
        def remove_item():
            v = option.get()
            if v == None:
                return
            for key in table.log.keys():
                if get_date_time_from_timestamp(key) == v:
                    key_to_remove = key
                    break
            del table.log[key_to_remove]
            self.focus_table(table.table_number)
            window.destroy()
            
        timestamps = list(table.log.keys())

        values = [f"{get_date_time_from_timestamp(timestamp)}" for timestamp in timestamps]
        values.insert(0, "None")
        option = customtkinter.CTkOptionMenu(window, values=values, command=None)
        option.pack(pady=30)

        execute_button = customtkinter.CTkButton(window, text="remove", command=remove_item)
        execute_button.pack(pady=20)

        cancel_button = customtkinter.CTkButton(window, text="cancel", command=cancel)
        cancel_button.pack(pady=20)

    def focus_table(self, number):
        self.focused_table_frame.destroy()
        self.focused_table_frame = customtkinter.CTkFrame(self.tabs.tab("tables"), width=580, height=400)
        self.focused_table_frame.grid(row=0, column=0, sticky="nsew")
        self.focused_table_frame.pack_propagate(False)

        t = None
        n = int(number)
        for table in self.tables:
            if table.table_number == n and table.state:
                t = table
                break
        if t == None:
            return
        
        headding = customtkinter.CTkLabel(self.focused_table_frame, text=f"Table {n:02d}", font=("open sans", 16))
        headding.grid(row=0, column=0)
        game = customtkinter.CTkLabel(self.focused_table_frame, text=f"{t.game}", font=("open sans", 16))
        game.grid(row=0, column=1)
        break_button = customtkinter.CTkButton(self.focused_table_frame, text="Send on bereak", command=lambda: self.send_on_break(timestamp=get_time_nearest_15(timestamp=True), table=t))
        close_button = customtkinter.CTkButton(self.focused_table_frame, text="Close table", command=lambda: self.close_table(t, time()))
        add_break = customtkinter.CTkButton(self.focused_table_frame, text="Add break", command=lambda:self.send_on_break(table=t))
        cancel_break = customtkinter.CTkButton(self.focused_table_frame, text="Undo break", command=lambda: self.remove_log_item(t))
        remove_table = customtkinter.CTkButton(self.focused_table_frame, text="Remove table", command=lambda: self.remove_table_completly(t))
        remove_table.grid(row=4, column=1)
        cancel_break.grid(row=4, column=0, padx=5, pady=5)
        break_button.grid(row=1, column=0, padx=5)
        close_button.grid(row=1, column=2, padx=5)
        add_break.grid(row=1, column=1, padx=5)

        try:
            prev_break = customtkinter.CTkLabel(self.focused_table_frame, text=f"Table last went on break {get_time_from_timestamp(max(t.breaks))}", font=("open sans", 16))
            prev_break.grid(row=2, column=0, columnspan=2)
        except ValueError:
            pass
        try:
            if t.breaks:
                nb = max(t.breaks)
                nb += globals.TOTAL_TIME
            else:
                nb = t.start_point + globals.MAX_PLAY_TIME
            next_break = customtkinter.CTkLabel(self.focused_table_frame, text=f"Next table break {get_time_from_timestamp(nb)}", font=("open sans", 16))
            next_break.grid(row=2, column=2, columnspan=2, padx=5)
        except ValueError:
            pass

        log = customtkinter.CTkScrollableFrame(self.focused_table_frame, label_text="Table log", width=240)
        for item in t.log:
            customtkinter.CTkLabel(log, text=f"{get_date_time_from_timestamp(item)}: {t.log[item]}").pack(pady=3)
        upcoming = customtkinter.CTkScrollableFrame(self.focused_table_frame, label_text="Upcoming breaks")
        for i in range(int(nb), int(nb+globals.DAY), int(globals.TOTAL_TIME)):
            customtkinter.CTkLabel(upcoming, text=f"{get_time_from_timestamp(i)}").pack(pady=3)

        log.grid(row=3, column=0, columnspan=2)
        upcoming.grid(row=3, column=2)


    def list_tables(self):
        self.refresh_table_list()
        if len(self.open_tables) == 0:
            return
        for table in sorted(self.open_tables):
            table_frame = customtkinter.CTkFrame(self.table_frames)
            customtkinter.CTkLabel(table_frame, text=f"Table: {table}", font=("open sans", 16)).grid(row=0, column=0)
            customtkinter.CTkButton(table_frame, text="focus", command=lambda n=table: self.focus_table(n), width=10).grid(row=0, column=1, padx=10)
            table_frame.pack(pady=5)

    def save_state(self):
        # create a small text file with a clue on wether we need to restore state from state.json
        with open("state.txt", "w") as file:
            file.write("yes")

        state = {
            "break sorter": {
                "date": self.break_sorter.date,
                "location": self.break_sorter.location
            },
            "tables": [
                {
                    "number": table.table_number,
                    "state": table.state,
                    "game": table.game,
                    "breaks": table.breaks,
                    "log": table.log,
                    "opened": table.opened,
                    "start_point": table.start_point
                }
                for table in self.tables
            ]
        }

        with open("state.json", "w") as file:
            json.dump(state, file)

    def check_state(self):
        try:
            with open("state.txt", "r") as file:
                content = file.read().strip()

            if content == "yes":
                self.load_state()
        except FileNotFoundError:
            return
        
    def load_state(self):
        ...



if __name__ == "__main__":
    app = App()
    app.mainloop()