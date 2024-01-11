import customtkinter
import tkinter

from util import Break_sorter, Table, Break_container

x = Break_sorter()
x.add_hours()

table_1 = Table(1, "Poker", timestamp=x.base)
table_2 = Table(2, "Blackjack", timestamp=x.base)
x.add_table(table_1)
x.add_table(table_2)


customtkinter.set_appearance_mode("dark")  # Modes: system (default), light, dark
customtkinter.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

root = customtkinter.CTk()

def r(display):
    display.configure(border_color="green")

    return

root.title("learning custom tkinter")
root.geometry("700x450")

frame = customtkinter.CTkScrollableFrame(root, label_text="Table Break List")
frame.pack(pady=40)

for hour in x.hours.keys():
    time_frame = customtkinter.CTkFrame(frame)
    time_frame.grid_columnconfigure((0, 1, 2, 3, 4), minsize=40)
    
    customtkinter.CTkLabel(time_frame, text=f"{hour[:5]}:", justify="left", font=("Open Sans", 24)).grid(row=0, column=0)
    if len(x.hours[hour]) > 0:
        n = 1
        for table in x.hours[hour]:
            if n == 1:
                table.send_on_scadualed_break()
            time_frame.grid_columnconfigure((0, 1, 2, 3, 4), minsize=15)
            rb = customtkinter.CTkRadioButton(time_frame, text="", state="disabled", height=10, width=10, border_width_unchecked=2)
            if table.sent == True:
                rb.configure(border_color="blue")
            rb.grid(row=n, column=0)
            customtkinter.CTkLabel(time_frame, text=f"table {table}", font=("Open Sans", 16)).grid(row=n, column=1)
            customtkinter.CTkButton(time_frame, text="Break", command=lambda d=rb: r(d), width=10).grid(row=n, column=3)
            time_frame.grid_rowconfigure(n, pad=10)
            n+=1
            

    time_frame.pack(pady=5)

root.mainloop()