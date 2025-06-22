from tkinter import *
from algorithm_selecrion import open_algorithm_selection
def open_data_path(data_input, root):
    data_input.withdraw()
    data_path = Toplevel(data_input)
    data_path.title("Data Path")
    data_path.geometry("800x500")
    data_path.configure(bg='#F5E0C8')

    Label(data_path,
          text="Input the absolute path of the .csv file",
          anchor=CENTER,
          bg='#E6B7A9',
          height=3,
          width=50,
          bd=3,
          font=("Arial", 16, "bold"),
          fg='black',
          relief=RAISED,
          wraplength=500).pack(pady=(100, 20))

    def Take_input():
        INPUT = inputtxt.get("1.0", "end-1c")
        print(INPUT)
        open_algorithm_selection(data_path, root, INPUT)

    inputtxt = Text(data_path,
                    height=3,
                    width=50,
                    bg="#D8A8C0",
                    fg='black',
                    font=("Arial", 12),
                    bd=3,
                    relief=RAISED,
                    padx=10,
                    pady=10)
    inputtxt.pack(pady=20)

    Display = Button(data_path,
                     height=2,
                     width=20,
                     text="Next",
                     command=Take_input,
                     bg='#E6B7A9',
                     fg='black',
                     font=("Arial", 12, "bold"),
                     bd=3,
                     relief=RAISED,
                     cursor="hand2")
    Display.pack(pady=10)

    def on_close():
        root.destroy()
        data_input.destroy()
        data_path.destroy()

    data_path.protocol("WM_DELETE_WINDOW", on_close)
