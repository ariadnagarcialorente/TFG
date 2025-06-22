from tkinter import *
from data_MAR import open_data_MAR  # Import the new MAR interface
from data_MCAR import open_data_MCAR 
from data_MNAR import open_data_MNAR 

def open_data_generator(data_input,root):
    data_input.withdraw()
    data_generator = Toplevel(data_input)
    data_generator.title("Data Generator")
    data_generator.geometry("800x500")
    data_generator.configure(bg='#F5E0C8')

    Label(data_generator,
          text="Choose Type of Data:",
          anchor=CENTER,
          bg='#E6B7A9',
          height=3,
          width=50,
          bd=3,
          font=("Arial", 16, "bold"),
          fg='black',
          relief=RAISED,
          wraplength=500).pack(pady=(150, 20))

    button_frame = Frame(data_generator, bg='#F5E0C8')
    button_frame.pack(pady=20)

    # Updated MAR button command
    Button(button_frame,
           text="MAR",
           command=lambda: open_data_MAR(data_generator, root),
           bg='#E6B7A9',
           height=2,
           width=20,
           bd=3,
           font=("Arial", 12, "bold"),
           cursor="hand2",
           fg='black',
           relief=RAISED).pack(side=LEFT, padx=10)

    Button(button_frame,
           text="MCAR",
           command=lambda: open_data_MCAR(data_generator, root),
           bg='#E6B7A9',
           height=2,
           width=20,
           bd=3,
           font=("Arial", 12, "bold"),
           cursor="hand2",
           fg='black',
           relief=RAISED).pack(side=LEFT, padx=10)
    
    Button(button_frame,
           text="MNAR",
           command=lambda: open_data_MNAR(data_generator, root),
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
        data_generator.destroy()

    data_generator.protocol("WM_DELETE_WINDOW", on_close)