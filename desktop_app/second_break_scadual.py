import customtkinter
import tkinter

customtkinter.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

from util import Break_sorter, Table, Break_container
from helpers import get_formatted_date, check_valid_date, get_time_nearest_15, get_timestamp
import globals

# x = Break_sorter()
# x.add_hours()

# table_1 = Table(1, "Poker", timestamp=x.base)
# table_2 = Table(2, "Blackjack", timestamp=x.base)
# x.add_table(table_1)
# x.add_table(table_2)

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        #app tools
        self.break_sorter = None
        self.tables = list()

        # configure window
        self.title("Poker table break sorter")
        self.geometry(f"{1100}x{580}")

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
        self.sidebar_button_3 = customtkinter.CTkButton(self.sidebar_frame, text="Somthing else", command=None)
        self.sidebar_button_3.grid(row=3, column=0, padx=20, pady=10)

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

        self.time_frames = customtkinter.CTkScrollableFrame(self.tabs.tab("dashboard"), label_text="Table Break List")
        self.time_frames.grid(row=0, column=1)

    def refresh_app(self):
        self.populate_timeframes()

    def start_break_sorter(self):
        ...

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
                self.refresh_app()
            except ValueError:
                error.configure(text="invalid date format")
            cancel()
                

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
            n = table_number.get()
            g = game.get()
            s = gdate.get()
            t = time.get()
            try:
                n = int(n)
                day, month, year = map(int, s.split('-'))
                hour, minute = map(int, t.split(':'))
                date = f"{year}-{month:02d}-{day:02d}"
                if check_valid_date(date) == False:
                    raise ValueError
                timestamp = get_timestamp(date, globals.LOCATION, h=hour, m=minute)
                table = Table(n, g, timestamp)
                if table in self.tables: #TODO fix this check
                    error.configure(test="table is already open")
                self.break_sorter.add_table(table)
                self.tables.append(table)
                self.refresh_app()
            except ValueError:
                error.configure(text="invalid date or time format, date must be <DD-MM-YYYY> and time must be <HH:MM>")

        label_1 = customtkinter.CTkLabel(window, text="Table number")
        label_1.pack(pady=5)
        table_number = customtkinter.CTkComboBox(window, values=globals.TABLES)
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
        
    def refresh_timeframes(self):
        if self.time_frames:
            self.time_frames.destroy()
        self.time_frames = customtkinter.CTkScrollableFrame(self.tabs.tab("dashboard"), label_text="Table Break List")
        self.time_frames.grid(row=0, column=1)
        
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
                    customtkinter.CTkLabel(time_frame, text=f"table {table}", font=("Open Sans", 16)).grid(row=n, column=1)
                    customtkinter.CTkButton(time_frame, text="Break", command=lambda d=rb: r(d), width=10).grid(row=n, column=3)
                    time_frame.grid_rowconfigure(n, pad=10)
                    n+=1
                    

            time_frame.pack(pady=5)


if __name__ == "__main__":
    app = App()
    app.mainloop()