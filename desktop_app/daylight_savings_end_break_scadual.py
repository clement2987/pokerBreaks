import customtkinter
import tkinter
from tkinter import messagebox, filedialog
from time import time
import datetime
from werkzeug.security import check_password_hash, generate_password_hash

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


customtkinter.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

from util import Break_sorter, Table, Break_container, DLS_end_break_sorter, DLS_start_break_sorter, Request_handler
from helpers import get_formatted_date, check_valid_date, get_time_nearest_15, get_timestamp, get_date_time_from_timestamp, get_time_from_timestamp, find_time_index, save_state_json, load_state_json, get_gaming_day_base, add_days_to_date
import globals


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        # self.check_password()

        #app tools
        self.break_sorter = None
        self.tables = list()
        self.closed_table_objects = list()

        self.closed_tables = globals.TABLES
        self.open_tables = list()

        self.requests = Request_handler()
        self.network_connected = False

        # configure window
        self.title("Poker BreakSync")
        self.geometry(f"{1150}x{640}")

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)

        # create sidebar frame with widgets
        button_width=170
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, height=1630, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="Main Menu", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        self.sidebar_button_1 = customtkinter.CTkButton(self.sidebar_frame, width=button_width,  text="Start break sorter", command=self.break_sorter_window)
        self.sidebar_button_1.grid(row=1, column=0, padx=20, pady=10)
        self.sidebar_button_2 = customtkinter.CTkButton(self.sidebar_frame, width=button_width,  text="Open Table", command=self.open_table)
        self.sidebar_button_2.grid(row=2, column=0, padx=20, pady=10)
        self.sidebar_button_3 = customtkinter.CTkButton(self.sidebar_frame, width=button_width,  text="Close all tables", command=self.close_all_tables)
        self.sidebar_button_3.grid(row=4, column=0, padx=20, pady=10)
        self.sidebar_button_4 = customtkinter.CTkButton(self.sidebar_frame, width=button_width,  text="Generate report and close", command=self.report_and_close)
        self.sidebar_button_4.grid(row=5, column=0, padx=20, pady=10)
        self.sidebar_button_5 = customtkinter.CTkButton(self.sidebar_frame, width=button_width,  text="Generate report and roll", command=self.report_and_role)
        self.sidebar_button_5.grid(row=6, column=0, padx=20, pady=10)
        self.sidebar_button_6 = customtkinter.CTkButton(self.sidebar_frame, width=button_width,  text="Quick close", command=self.destroy)
        self.sidebar_button_6.grid(row=7, column=0, padx=20, pady=10)
        self.sidebar_button_7 = customtkinter.CTkButton(self.sidebar_frame, width=button_width,  text="Full close", command=self.close_app)
        self.sidebar_button_7.grid(row=8, column=0, padx=20, pady=10)
        # self.sidebar_button_8 = customtkinter.CTkButton(self.sidebar_frame, width=button_width,  text="temp", command=self.send_table_list)
        # self.sidebar_button_8.grid(row=9, column=0, padx=20, pady=10)
        # self.sidebar_button_9 = customtkinter.CTkButton(self.sidebar_frame, width=button_width,  text="get breaks", command=self.get_breaks_from_server)
        # self.sidebar_button_9.grid(row=10, column=0, padx=20, pady=10)
        # self.sidebar_button_10 = customtkinter.CTkButton(self.sidebar_frame, width=button_width,  text="send recipt", command=self.send_activation_code)
        # self.sidebar_button_10.grid(row=11, column=0, padx=20, pady=10)

        #create tabs
        self.tabs = customtkinter.CTkTabview(self, width=900, height=560)
        self.tabs.grid(row=0, column=1)
        self.tabs.add("dashboard")
        self.tabs.add("tables")
        self.tabs.add("network")
        self.tabs.add("settings")
        self.tabs.add("help")

        #dashboard
        self.tabs.tab("dashboard").grid_columnconfigure(0, minsize=590)
        self.tabs.tab("dashboard").grid_columnconfigure(1, minsize=300)
        self.tabs.tab("dashboard").grid_rowconfigure(0, minsize=400)
        self.tabs.tab("dashboard").grid_rowconfigure(1, minsize=150)

        self.time_frames = customtkinter.CTkScrollableFrame(self.tabs.tab("dashboard"), label_text="Table Break List", height=380)
        self.time_frames.grid(row=0, column=1)
        self.time_frame_children = list()

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
        self.alert = customtkinter.CTkLabel(self.alerts, text="No alerts", font=("Open Sans", 20), width=400, height=20)
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

        #network
        self.tabs.tab("network").grid_columnconfigure(0, minsize=590)
        self.tabs.tab("network").grid_columnconfigure(1, minsize=300)
        self.tabs.tab("network").grid_rowconfigure(0, minsize=400)
        self.tabs.tab("network").grid_rowconfigure(1, minsize=150)

        self.network_log = customtkinter.CTkScrollableFrame(self.tabs.tab("network"), label_text="Event log", height=380, width=500)
        self.network_log.grid(row=0, column=0)

        self.network_officers = customtkinter.CTkFrame(self.tabs.tab("network"), width=300, height=400)
        self.network_officers.grid(row=0, column=1, sticky="nsew")
        customtkinter.CTkButton(self.network_officers, text="Refresh", command=self.get_active_users).pack(pady=5)

        self.network_status_frame = customtkinter.CTkFrame(self.tabs.tab("network"), width=580, height=140)
        self.network_status_frame.grid(row=1, column=0)
        self.network_status = customtkinter.CTkLabel(self.network_status_frame, text="disconected", font=("Open Sans", 20), width=400, height=20)
        self.network_status.pack(pady=10, expand=0)

        self.network_code = customtkinter.CTkFrame(self.tabs.tab("network"), height=110, width=300)
        self.network_code.grid(row=1, column=1)
        self.current_code = customtkinter.CTkLabel(self.network_code, text="")
        self.current_code.pack()
        customtkinter.CTkButton(self.network_code, text="Set Activation Code", command=self.send_activation_code).pack(pady=5)

        # settings
        self.tabs.tab("settings").grid_columnconfigure(0, minsize=200)
        self.tabs.tab("settings").grid_columnconfigure(1, minsize=300)
        self.tabs.tab("settings").grid_columnconfigure(2, minsize=300)
        # self.tabs.tab("settings").grid_rowconfigure(0, minsize=400)
        # self.tabs.tab("settings").grid_rowconfigure(1, minsize=150)

        self.setting_button_0 = customtkinter.CTkButton(self.tabs.tab("settings"), text="change", command=self.browse_files)
        self.setting_button_0.grid(row=0, column=0, pady=10)
        self.setting_setting_0 = customtkinter.CTkLabel(self.tabs.tab("settings"), text="Destination folder for reports")
        self.setting_setting_0.grid(row=0, column=1, pady=10)
        self.setting_value_0 = customtkinter.CTkLabel(self.tabs.tab("settings"), text=globals.settings['reports_file'])
        self.setting_value_0.grid(row=0, column=2, pady=10)

        self.setting_button_1 = customtkinter.CTkButton(self.tabs.tab("settings"), text="change", command=self.change_break_time)
        self.setting_button_1.grid(row=1, column=0, pady=10)
        self.setting_setting_1 = customtkinter.CTkLabel(self.tabs.tab("settings"), text="Break times")
        self.setting_setting_1.grid(row=1, column=1, pady=10)
        self.setting_value_1 = customtkinter.CTkLabel(self.tabs.tab("settings"), text=f"{int(globals.settings['times']['break'])//60} minutes")
        self.setting_value_1.grid(row=1, column=2, pady=10)

        self.setting_button_2 = customtkinter.CTkButton(self.tabs.tab("settings"), text="change", command=self.change_play_time)
        self.setting_button_2.grid(row=2, column=0, pady=10)
        self.setting_setting_2 = customtkinter.CTkLabel(self.tabs.tab("settings"), text="Max time playing")
        self.setting_setting_2.grid(row=2, column=1, pady=10)
        self.setting_value_2 = customtkinter.CTkLabel(self.tabs.tab("settings"), text=f"{int(globals.settings['times']['btwn_break'])//60} minutes")
        self.setting_value_2.grid(row=2, column=2, pady=10)

        self.setting_button_3 = customtkinter.CTkButton(self.tabs.tab("settings"), text="change", command=self.change_tables)
        self.setting_button_3.grid(row=3, column=0, pady=10)
        self.setting_setting_3 = customtkinter.CTkLabel(self.tabs.tab("settings"), text="Tables")
        self.setting_setting_3.grid(row=3, column=1, pady=10)
        self.setting_value_3 = customtkinter.CTkLabel(self.tabs.tab("settings"), text=globals.settings['tables'], wraplength=300)
        self.setting_value_3.grid(row=3, column=2, pady=10)

        self.setting_button_4 = customtkinter.CTkButton(self.tabs.tab("settings"), text="change", command=self.change_games)
        self.setting_button_4.grid(row=4, column=0, pady=10)
        self.setting_setting_4 = customtkinter.CTkLabel(self.tabs.tab("settings"), text="Games")
        self.setting_setting_4.grid(row=4, column=1, pady=10)
        self.setting_value_4 = customtkinter.CTkLabel(self.tabs.tab("settings"), text="".join(f" {game} " for game in globals.settings['game_type']), wraplength=300)
        self.setting_value_4.grid(row=4, column=2, pady=10)

        self.setting_button_5 = customtkinter.CTkButton(self.tabs.tab("settings"), text="change", command=self.change_domain)
        self.setting_button_5.grid(row=5, column=0, pady=10)
        self.setting_setting_5 = customtkinter.CTkLabel(self.tabs.tab("settings"), text="Network domain")
        self.setting_setting_5.grid(row=5, column=1, pady=10)
        self.setting_value_5 = customtkinter.CTkLabel(self.tabs.tab("settings"), text=globals.settings['domain'])
        self.setting_value_5.grid(row=5, column=2, pady=10)

        self.setting_button_6 = customtkinter.CTkButton(self.tabs.tab("settings"), text="change", command=self.change_password)
        self.setting_button_6.grid(row=6, column=0, pady=10)
        self.setting_setting_6 = customtkinter.CTkLabel(self.tabs.tab("settings"), text="Password")
        self.setting_setting_6.grid(row=6, column=1, pady=10)
        self.setting_value_6 = customtkinter.CTkLabel(self.tabs.tab("settings"), text=f"{self.get_password()[:20]}")
        self.setting_value_6.grid(row=6, column=2, pady=10)

        self.check_state()

    def check_password(self):
        password_hash = self.get_password()
        check_password = False
        
        while check_password == False:
            dialog = customtkinter.CTkInputDialog(text="Type in a number:", title="Test", show='•')        
            password = dialog.get_input()
            if password == None:
                exit()
            check_password = check_password_hash(password_hash, password)
            
        return

    def get_password(self):
        with open("password.txt", 'r') as password_file:
            password = password_file.read().strip()
            return password
        
    def change_password(self):
        window = customtkinter.CTkToplevel(self)
        window.title("change password")
        window.geometry("700x450")
        window.grab_set()

        def cancel():
            window.destroy()

        def change_password_now():
            old_password_hash = self.get_password()
            if check_password_hash(old_password_hash, old_password.get()) != True:
                error.configure(text="incorrect password")
                return
            pass1 = new_password.get()
            pass2 = re_new_password.get()
            if pass1 != pass2:
                error.configure(text="passwords do not match")
                return
            new_password_hash = generate_password_hash(pass1)
            with open("password.txt", "w") as password_file:
                password_file.write(new_password_hash)
                error.configure(text="password changed successfully")

        error = customtkinter.CTkLabel(window, text="")
        error.pack(pady=10)

        old_password_label = customtkinter.CTkLabel(window, text="old password")
        old_password_label.pack(pady=10)
        old_password = customtkinter.CTkEntry(window, show="•")
        old_password.pack()

        new_password_label = customtkinter.CTkLabel(window, text="new password")
        new_password_label.pack(pady=10)
        new_password = customtkinter.CTkEntry(window, show="•")
        new_password.pack()

        re_new_password_label = customtkinter.CTkLabel(window, text="re-type new password")
        re_new_password_label.pack(pady=10)
        re_new_password = customtkinter.CTkEntry(window, show="•")
        re_new_password.pack()        

        start_button = customtkinter.CTkButton(window, text="change password", command=change_password_now)
        start_button.pack(pady=10)
        cancel_button = customtkinter.CTkButton(window, text="cancel", command=cancel)
        cancel_button.pack()


    def refresh_app(self):
        self.populate_timeframes()
        self.list_tables()
        self.populate_main_display(time())
        self.save_state()
        if self.network_connected == True:
            self.send_table_list()

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
            self.alert.configure(text="No alerts")
        elif alert[0] == " ":
            self.alert.configure(text="The following tables are late for break"+alert)
        else:
            self.alert.configure(text=alert)
        
        if current_time.minute in [0, 15, 30, 45]:
            self.populate_main_display(current_timestamp)


        

        self.after(1000, self.time_check)

    def network_auto(self):
        if self.network_connected == True:
            self.get_breaks_from_server()
        self.after(1000*300, self.network_auto)

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
                self.break_sorter = DLS_end_break_sorter(date, location=globals.LOCATION)
                self.break_sorter.add_hours()
                if len(self.tables) > 0:
                    for table in self.tables:
                        self.break_sorter.add_table(table)
                self.add_timeframes()
                self.start_network_app()
                self.refresh_app()
                self.date_label.configure(text=s)
                self.populate_main_display(time())
                
                self.network_auto()
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

    def check_if_table_exists(self, number):
        for table in self.tables:
            if table.state == "closed" and table.table_number == number:
                return table
        return None

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
                
                if tn in self.open_tables: 
                    error.configure(test="table is already open")
                    return
                temp = self.check_if_table_exists(n)
                if temp:
                    table = temp
                    table.reopen_table(timestamp + gaming_date_offset, g)
                else:
                    table = Table(n, g, timestamp + gaming_date_offset)
                    self.tables.append(table)
                if self.break_sorter:
                    self.break_sorter.add_table(table)
                
                self.closed_tables.remove(tn)
                self.open_tables.append(tn)
                table_number.configure(values=self.closed_tables)
                if len(self.closed_tables) > 0:
                    table_number.set(self.closed_tables[0])
                self.refresh_app()
                error.configure(text=f"Table{tn} opened ad {g}")
            except ValueError as e:
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

    def send_on_break(self, timestamp=None, break_container=None, table=None, rrr=None):
        if rrr:
            rrr.configure(border_color="green")
        if break_container != None:
            break_container.send_on_scadualed_break()
            self.save_state()
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
        for time_frame in self.time_frame_children:
            children = time_frame.winfo_children()
            if len(children) > 1:
                for widget in children[1:]:
                    widget.destroy()
                time_frame.grid_columnconfigure((0, 1, 2, 3, 4), minsize=40)

    def populate_main_display(self, timestamp):
        if not self.break_sorter:
            return
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
        
        self.table_break_buttons = dict()
        for hour in self.break_sorter.hours.keys():
            
            if len(self.break_sorter.hours[hour]) > 0:
                time_frame = self.time_frame_children[find_time_index(hour[:5])]
                n = 1
                for table in self.break_sorter.hours[hour]:
                    time_frame.grid_columnconfigure((0, 1, 2, 3, 4), minsize=15)
                    rb = customtkinter.CTkRadioButton(time_frame, text="", state="disabled", height=10, width=10, border_width_unchecked=2)
                    
                    rb.grid(row=n, column=0)
                    if table.sent:
                        rb.configure(border_color="green")
                    customtkinter.CTkLabel(time_frame, text=f"table {table}", font=("Open Sans", 16)).grid(row=n, column=1)
                    break_button = customtkinter.CTkButton(time_frame, text="Break", command=lambda t=table, rad=rb: self.send_on_break(break_container=t, rrr=rad), width=10)
                    break_button.grid(row=n, column=3)
                    self.table_break_buttons[f"{hour[:5]}{table}"] = break_button
                    time_frame.grid_rowconfigure(n, pad=10)
                    n+=1                    

            

    def add_timeframes(self):
        if self.break_sorter == None:
            return
        for hour in self.break_sorter.hours.keys():
            time_frame = customtkinter.CTkFrame(self.time_frames)
            time_frame.grid_columnconfigure((0, 1, 2, 3, 4), minsize=40)

            customtkinter.CTkLabel(time_frame, text=f"{hour[:5]}:", justify="left", font=("Open Sans", 24)).grid(row=0, column=0)
            time_frame.pack(pady=5)
            self.time_frame_children.append(time_frame)

    def refresh_table_list(self):
        if self.table_frames:
            self.table_frames.destroy()
        self.table_frames = customtkinter.CTkScrollableFrame(self.tabs.tab("tables"), label_text="open table List", height=380)
        self.table_frames.grid(row=0, column=1)

    def send_table_on_unscadualed_break(self, date, time):
        ...

    def close_table(self, table, timestamp):
        if table.state == "closed":
            return
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




    # settings
    def browse_files(self):
        file_path = filedialog.askdirectory(initialdir="/", title="Select Folder")

        globals.settings["reports_file"] = file_path
        globals.save_settings(globals.settings)
        self.setting_value_0.configure(text=file_path)

    def change_break_time(self):
        while True:
            dialog = customtkinter.CTkInputDialog(text="How many minutes is the break? Note break time must be evenly devisable by 60", title="Change break time")
            responce = dialog.get_input()
            if responce == None:
                return
            try:
                break_time = int(responce.strip())
                if 60%break_time != 0:
                    continue
                globals.settings['times']['break'] = str(break_time*60)
                self.setting_value_1.configure(text=f"{int(globals.settings['times']['break'])//60} minutes")
                globals.save_settings(globals.settings)
                break

            except ValueError:
                continue

    def change_play_time(self):
        while True:
            dialog = customtkinter.CTkInputDialog(text="How long can the table sat open for between breaks in minutes?", title="Change play time")
            responce = dialog.get_input()
            if responce == None:
                return
            try:
                break_time = int(responce.strip())
                
                globals.settings['times']['btwn_break'] = str(break_time*60)
                self.setting_value_2.configure(text=f"{int(globals.settings['times']['btwn_break'])//60} minutes")
                globals.save_settings(globals.settings)
                break

            except ValueError:
                continue

    def change_domain(self):
        dialog = customtkinter.CTkInputDialog(text="What is the new domain for the network", title="Change network domain")
        responce = dialog.get_input()
        if responce == None:
            return
        globals.settings['domain'] = responce.strip()
        globals.save_settings(globals.settings)
        self.setting_value_5.configure(text=globals.settings['domain'])

    def change_tables(self):
        window = customtkinter.CTkToplevel(self)
        window.title("Edit tables")
        window.geometry("700x450")
        window.grab_set()

        def settings_remove_table():
            to_be_removed = table_number.get()
            globals.settings['tables'].remove(to_be_removed)
            globals.save_settings(globals.settings)
            table_number.configure(values=globals.settings['tables'])
            table_number.set(globals.settings['tables'][0])

        def settings_add_table():
            to_be_added = add_table_entry.get()
            try:
                to_be_added = int(to_be_added)
                to_be_added = f"{to_be_added:02d}"
            except ValueError:
                return
            globals.settings['tables'].append(to_be_added)
            globals.settings['tables'] = sorted(globals.settings['tables'])
            globals.save_settings(globals.settings)
            table_number.configure(values=globals.settings['tables'])

        def close_window():
            self.setting_value_3.configure(text=globals.settings['tables'])
            window.destroy()

        table_number = customtkinter.CTkOptionMenu(window, values=globals.settings['tables'])
        table_number.pack(pady=20)
        remove_button = customtkinter.CTkButton(window, text="remove table", command=settings_remove_table)
        remove_button.pack(pady=10)

        add_table_entry = customtkinter.CTkEntry(window, placeholder_text="table number")
        add_table_entry.pack(pady=10)
        add_button = customtkinter.CTkButton(window, text="add table", command=settings_add_table)
        add_button.pack(pady=10)

        close_button = customtkinter.CTkButton(window, text="close", command=close_window)
        close_button.pack(pady=10)

    def change_games(self):
        window = customtkinter.CTkToplevel(self)
        window.title("Edit games")
        window.geometry("700x450")
        window.grab_set()

        def remove_game():
            to_be_removed = table_number.get()
            globals.settings['game_type'].remove(to_be_removed)
            globals.save_settings(globals.settings)
            table_number.configure(values=globals.settings['game_type'])
            table_number.set(globals.settings['game_type'][0])

        def add_game():
            to_be_added = add_table_entry.get()
            
            globals.settings['game_type'].append(to_be_added)
            globals.settings['game_type'] = sorted(globals.settings['game_type'])
            globals.save_settings(globals.settings)
            table_number.configure(values=globals.settings['game_type'])

        def close_window():
            self.setting_value_4.configure(text="".join(f" {game} " for game in globals.settings['game_type']))
            window.destroy()

        table_number = customtkinter.CTkOptionMenu(window, values=globals.settings['game_type'])
        table_number.pack(pady=20)
        remove_button = customtkinter.CTkButton(window, text="remove game", command=remove_game)
        remove_button.pack(pady=10)

        add_table_entry = customtkinter.CTkEntry(window, placeholder_text="game")
        add_table_entry.pack(pady=10)
        add_button = customtkinter.CTkButton(window, text="add game", command=add_game)
        add_button.pack(pady=10)

        close_button = customtkinter.CTkButton(window, text="close", command=close_window)
        close_button.pack(pady=10)



    #main function list

    def close_all_tables(self):
        timestamp = time()
        for table in self.tables:
            self.close_table(table, timestamp)

    def report_and_close(self):
        self.close_all_tables()
        self.generate_report()
        self.close_app()

    def report_and_role(self):
        self.generate_report()
        self.roll_gaming_day()

    def roll_gaming_day(self):
        if self.break_sorter == None:
            return
        date = add_days_to_date(self.break_sorter.date, 1)
        location = self.break_sorter.location
        self.break_sorter = DLS_end_break_sorter(date, location)
        self.break_sorter.add_hours()
        tables_to_remove = list()
        for table in self.tables:
            if table.state == "open":
                table.log = dict()
                table.log[get_gaming_day_base(date, location)] = "Table rolled from previous day"
                self.break_sorter.add_table(table)
            else:
                tables_to_remove.append(table)
        for table in tables_to_remove:
            self.tables.remove(table)

        self.refresh_app()
        year, month, day = self.break_sorter.date.split('-')
        s = f"{day}-{month}-{year}"
        self.date_label.configure(text=s)

    def save_state(self):
        # create a small text file with a clue on wether we need to restore state from state.json
        if not self.break_sorter:
            return
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

        save_state_json(state)

        

    def check_state(self):
        try:
            with open("state.txt", "r") as file:
                content = file.read().strip()

            if content == "yes":
                self.load_state()
        except FileNotFoundError:
            return
        
    def load_state(self):
        state = load_state_json()
        # recreate all tables from saved file
        for table in state["tables"]:
            app_table = Table(table["number"], table["game"], table["opened"])
            if table["state"] == "closed":
                app_table.state = "closed"
            else:
                string_number = f"{table['number']:02d}"
                if string_number not in self.closed_tables:
                    print(string_number, self.closed_tables)
                self.closed_tables.remove(string_number)
                self.open_tables.append(string_number)
            app_table.start_point = table["start_point"]
            app_table.breaks = table["breaks"]
            for key in table["log"].keys():
                real = float(key)
                app_table.log[real] = table["log"][key]
            self.tables.append(app_table)

        # restore break sorter
        self.break_sorter = DLS_end_break_sorter(state["break sorter"]["date"], state["break sorter"]["location"])
        self.break_sorter.add_hours()
        if len(self.tables) > 0:
            for table in self.tables:
                self.break_sorter.add_table(table)
        self.add_timeframes()
        self.start_network_app()
        self.refresh_app()
        full_date = state["break sorter"]["date"]
        year, month, day = full_date.split("-")
        self.date_label.configure(text=f"{day}-{month}-{year}")
        self.populate_main_display(time())        
        self.network_auto()
        self.time_check()

    def close_app(self):
        with open("state.txt", "w") as file:
            file.write("no")
            self.destroy()

    def generate_report(self):
        if self.break_sorter is None:
            return

        # Set filename and file path for the report output
        file_name = f"{globals.settings['reports_file']}/Table-break-report-{self.break_sorter.date}.pdf"

        # Create a PDF document
        pdf_document = SimpleDocTemplate(file_name, pagesize=letter)

        # Content for the PDF
        content = []

        # Add date to the heading
        styles = getSampleStyleSheet()
        heading = Paragraph(f"<b>Report for {self.break_sorter.date}</b>", styles['Heading1'])
        content.append(heading)

        # Add table logs
        styles.add(ParagraphStyle(name='TableHeading', fontSize=12, fontName='Helvetica-Bold'))
        styles.add(ParagraphStyle(name='pdf_std', fontSize=12, fontName='Helvetica'))

        for table in self.tables:
            # Add table number as a subheading
            table_heading = Paragraph(f"<b>Table 33{table.table_number:02d}</b>", styles['TableHeading'])
            content.append(table_heading)

            # Add log entries for the table
            for timestamp, event in table.log.items():
                log_entry = Paragraph(f"{get_date_time_from_timestamp(timestamp)}: {event}", styles['pdf_std'])
                content.append(log_entry)

            # Add some space between tables
            content.append(Spacer(1, 15))

        # Build the PDF document
        pdf_document.build(content)

    
    # Network communication
    def log(self, item):
        customtkinter.CTkLabel(self.network_log, text=item).pack()


    def send_table_list(self):
        
        if self.break_sorter == None:
            return
        self.log("updating server with current state")
        table_list = dict()
        for hour in self.break_sorter.hours.keys():
            table_list[f"{hour[:5]}"] = list()
            for table in self.break_sorter.hours[hour]:
                table_dict = {
                    "number": table.table.table_number,
                    "break_confirmed": table.sent
                }
                table_list[f"{hour[:5]}"].append(table_dict)
        self.log(self.requests.send_breaks(table_list))

    def get_breaks_from_server(self):
        if self.break_sorter == None:
            return
        self.log("sending runner to check for break update")
        response = self.requests.update_breaks_from_officers()
        if response[0] == "new breaks attatched":
            for table_break in response[1]:
                t, n = table_break.split(" ")
                n = int(n)
                n = f"{n:02d}" #TODO this might be a problem
                button = self.table_break_buttons.get(f"{t}{n}")

                if button is not None:
                    button.invoke()
            self.send_recipt_to_server()
        self.log("runners report:")
        self.log(response[0])

    def send_recipt_to_server(self):
        if self.break_sorter == None:
            return
        self.log("runner returning to server to confirm receipt of breaks")
        
        self.log(self.requests.confirm_to_server())


    def send_activation_code(self):
        dialog = customtkinter.CTkInputDialog(text="what activation code do you want to use", title="Set activation code")
        response = dialog.get_input()
        if response == None:
            return
        self.log("sending activation code")
        self.log(self.requests.set_code(response))
        self.current_code.configure(text=response)
        


    def get_active_users(self):
        self.log("getting list of currently active users")
        response = self.requests.get_active_users()
        self.log(response[0])
        if response[0] == "active users attached attatched":
            self.network_officers.destroy()
            self.network_officers = customtkinter.CTkFrame(self.tabs.tab("network"), width=300, height=400)
            self.network_officers.grid(row=0, column=1, sticky="nsew")
            customtkinter.CTkButton(self.network_officers, text="Refresh", command=self.get_active_users).pack(pady=5)
            for user in response[1]:
                customtkinter.CTkLabel(self.network_officers, text=user).pack(pady=5)

    def start_network_app(self):
        self.log("attempted to access server")
        response = self.requests.login()
        self.log(response)
        if response == "App started successfully!":
            self.network_status.configure(text="connected")
            self.network_connected = True



if __name__ == "__main__":
    app = App()
    app.mainloop()