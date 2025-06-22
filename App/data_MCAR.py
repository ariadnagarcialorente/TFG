import tkinter as tk
from tkinter import messagebox
import subprocess
import threading
import os
import sys
from algorithm_selecrion import open_algorithm_selection

def open_data_MCAR(parent, root):
    parent.withdraw()
    data_MCAR = tk.Toplevel(parent)
    data_MCAR.title("MCAR Data Configuration")
    data_MCAR.geometry("600x500")  # Smaller window size
    data_MCAR.configure(bg='#F5E0C8')
    
    # Function to handle window closing
    def on_close():
        data_MCAR.destroy()
        parent.destroy()
        root.destroy()
    
    data_MCAR.protocol("WM_DELETE_WINDOW", on_close)
    
    # Main container frame
    main_frame = tk.Frame(data_MCAR, bg='#F5E0C8')
    main_frame.pack(fill="both", expand=True, padx=30, pady=30)
    
    # Title
    tk.Label(main_frame, text="MCAR Data Configuration", 
            bg='#F5E0C8', font=("Arial", 16, "bold")).pack(pady=10)
    
    # Dataset Parameters
    dataset_frame = tk.LabelFrame(main_frame, text="Dataset Parameters", bg='#F5E0C8', 
                                font=("Arial", 12), padx=10, pady=10)
    dataset_frame.pack(fill="x", pady=10)
    
    # Create parameter rows
    def create_param_row(frame, label, default, example, row):
        # Main label
        tk.Label(frame, text=label, bg='#F5E0C8', anchor="w", 
                font=("Arial", 10)).grid(row=row, column=0, padx=5, pady=5, sticky="w")
        
        # Entry field
        var = tk.StringVar(value=default)
        entry = tk.Entry(frame, textvariable=var, bg='#D8A8C0', 
                        font=("Arial", 10), width=15)
        entry.grid(row=row, column=1, padx=5, pady=5, sticky="e")
        
        # Example text below
        tk.Label(frame, text=example, bg='#F5E0C8', anchor="w", 
               fg="#666666", font=("Arial", 9)).grid(row=row+1, column=0, columnspan=2, padx=5, sticky="w")
        
        return var
    
    # Create dataset parameter rows
    rows_var = create_param_row(dataset_frame, "Number of Rows:", "10000", 
                               "Example: 10000", 0)
    cols_var = create_param_row(dataset_frame, "Number of Columns:", "20", 
                              "Example: 20", 2)
    
    # MCAR Parameters
    mcar_frame = tk.LabelFrame(main_frame, text="MCAR Parameters", bg='#F5E0C8', 
                             font=("Arial", 12), padx=10, pady=10)
    mcar_frame.pack(fill="x", pady=10)
    
    # Create MCAR parameter rows
    num_cols_var = create_param_row(mcar_frame, "Columns to Erase:", "5", 
                                   "Example: 5 (random columns will be selected)", 0)
    perc_var = create_param_row(mcar_frame, "Erase Percentage:", "20", 
                              "Example: 20 (20% of values in each column)", 2)
    
    # Button frame
    button_frame = tk.Frame(main_frame, bg='#F5E0C8')
    button_frame.pack(pady=20)
    
    # Function to execute commands
    def execute_commands():
        try:
            # Get parameters
            rows = int(rows_var.get())
            cols = int(cols_var.get())
            num_erase_cols = int(num_cols_var.get())
            percentage = float(perc_var.get())
            
            if rows <= 0 or cols <= 0:
                raise ValueError("Rows and columns must be positive integers")
            
            if num_erase_cols <= 0:
                raise ValueError("Number of columns to erase must be at least 1")
                
            if percentage <= 0 or percentage > 100:
                raise ValueError("Erase percentage must be between 0.1 and 100")
            
            # Generate complete dataset
            gen_script = "dataset_generator_numerical.py"
            if not os.path.exists(gen_script):
                gen_script = os.path.join(os.path.dirname(__file__), gen_script)
            
            gen_cmd = [
                sys.executable, gen_script,
                "--rows", str(rows),
                "--columns", str(cols),
                "--output", "complete_dataset.csv"
            ]
            subprocess.run(gen_cmd, check=True)
            
            # Apply MCAR rule
            mcar_script = "erase_generator_MCAR_GPU.py"
            if not os.path.exists(mcar_script):
                mcar_script = os.path.join(os.path.dirname(__file__), mcar_script)
            
            mcar_cmd = [
                sys.executable, mcar_script,
                "--input", "complete_dataset.csv",
                "--num_columns", str(num_erase_cols),
                "--percentage", str(percentage),
                "--output", "MCAR_dataset.csv",
                "--gpu"
            ]
            
            # Run MCAR process
            result = subprocess.run(mcar_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                messagebox.showinfo("Success", "MCAR dataset created successfully!")
            else:
                messagebox.showerror("Error", f"MCAR process failed:\n{result.stderr}")
            
            open_algorithm_selection(data_MCAR, root, "MCAR_dataset.csv")
        
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            generate_btn.config(state="normal")
            data_MCAR.config(cursor="")
    
    # Function to start processing
    def start_processing():
        generate_btn.config(state="disabled")
        data_MCAR.config(cursor="watch")
        threading.Thread(target=execute_commands, daemon=True).start()
    
    # Generate button
    generate_btn = tk.Button(button_frame, text="Generate MCAR Dataset", 
                            command=start_processing, bg='#E6B7A9', 
                            font=("Arial", 12, "bold"), width=20)
    generate_btn.pack(side=tk.LEFT, padx=10)
    
    # Back button
    back_btn = tk.Button(button_frame, text="Back", command=on_close, 
                        bg='#E6B7A9', font=("Arial", 12, "bold"))
    back_btn.pack(side=tk.LEFT, padx=10)