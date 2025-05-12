from tkinter import *
from data_path import open_data_path  # Import the next window
from data_generator import open_data_generator  # Import the next window

def open_data_input(root):
    root.withdraw()
    data_input = Toplevel(root)
    data_input.title("Data Input")
    data_input.geometry("800x500")
    data_input.configure(bg='#F5E0C8')

    Label(data_input,
          text="Input Data:",
          anchor=CENTER,
          bg='#E6B7A9',
          height=3,
          width=50,
          bd=3,
          font=("Arial", 16, "bold"),
          fg='black',
          relief=RAISED,
          wraplength=500).pack(pady=(150, 20))

    button_frame = Frame(data_input, bg='#F5E0C8')
    button_frame.pack(pady=20)

    Button(button_frame,
           text="I want to generate data",
           command=lambda: open_data_generator(data_input, root),  # Pass both parents
           bg='#E6B7A9',
           height=2,
           width=20,
           bd=3,
           font=("Arial", 12, "bold"),
           cursor="hand2",
           fg='black',
           relief=RAISED).pack(side=LEFT, padx=10)

    Button(button_frame,
           text="I have my own data",
           command=lambda: open_data_path(data_input, root),  # Pass both parents
           bg='#E6B7A9',
           height=2,
           width=20,
           bd=3,
           font=("Arial", 12, "bold"),
           cursor="hand2",
           fg='black',
           relief=RAISED).pack(side=LEFT, padx=10)

    def on_close():
        root.destroy()
        data_input.destroy()

    data_input.protocol("WM_DELETE_WINDOW", on_close)
