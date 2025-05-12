from tkinter import *
from data_input import open_data_input  # Import your custom function

root = Tk()
root.geometry("800x500")
root.title("Welcome to my app")
root.configure(bg='#F5E0C8')

text_var = StringVar()
text_var.set("Delete me but don't erase my information")

label = Label(root, 
              textvariable=text_var,
              anchor=CENTER,
              bg='#E6B7A9',
              height=3,
              width=50,
              bd=3,
              font=("Arial", 16, "bold"),
              fg='black',
              relief=RAISED,
              wraplength=500)
label.pack(pady=(150, 20))

button = Button(root,
                text="Click here to START",
                command=lambda: open_data_input(root),  # Pass root as argument
                bg='#E6B7A9',
                height=2,
                width=25,
                bd=3,
                font=("Arial", 12, "bold"),
                cursor="hand2",
                fg='black',
                relief=RAISED)
button.pack(pady=10)

root.mainloop()