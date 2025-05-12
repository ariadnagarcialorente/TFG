from tkinter import *

def open_data_input():

    def open_data_path():
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
            wraplength=500         
            ).pack(pady=(100, 20))
        
        def Take_input():
            INPUT = inputtxt.get("1.0", "end-1c")
            print(INPUT)  # You can replace this with any processing logic

        # Input Text Box with richer pink tone
        inputtxt = Text(data_path,
                        height=3,
                        width=50,
                        bg="#D8A8C0",         # More intense version of #F1DEEE
                        fg='black',
                        font=("Arial", 12),
                        bd=3,
                        relief=RAISED,
                        padx=10,
                        pady=10)

        # Pack input box
        inputtxt.pack(pady=20)

        # Next Button styled like others
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

        # Pack button
        Display.pack(pady=10)

        # Closing comands
        def on_close():
            root.destroy()  # Fully exit app
            data_input.destroy()
            data_path.destroy()
        data_path.protocol("WM_DELETE_WINDOW", on_close)
        

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
          wraplength=500         
        ).pack(pady=(150, 20))
    
    # Create a Frame to hold the buttons side by side
    button_frame = Frame(data_input, bg='#F5E0C8')
    button_frame.pack(pady=20)

    # First button
    Button(button_frame, 
           text="I want to generate data", 
           command=lambda: print("Button 1 clicked"),
           bg='#E6B7A9',      
           height=2,              
           width=20,              
           bd=3,                  
           font=("Arial", 12, "bold"), 
           cursor="hand2",   
           fg='black',             
           relief=RAISED
         ).pack(side=LEFT, padx=10)

    # Second button
    Button(button_frame, 
           text="I have my own data", 
           command=open_data_path,
           bg='#E6B7A9',      
           height=2,              
           width=20,              
           bd=3,                  
           font=("Arial", 12, "bold"), 
           cursor="hand2",   
           fg='black',             
           relief=RAISED
         ).pack(side=LEFT, padx=10)
    
    # Closing comands
    def on_close():
        root.destroy()  # Fully exit app
        data_input.destroy()
    data_input.protocol("WM_DELETE_WINDOW", on_close)
    



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
              wraplength=500         
            )
label.pack(pady=(150, 20)) 

button = Button(root, 
                text="Click here to START", 
                command=open_data_input,
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
