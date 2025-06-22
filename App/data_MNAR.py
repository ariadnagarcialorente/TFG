import tkinter as tk
from tkinter import messagebox
import subprocess
import threading
import os
import sys
from algorithm_selecrion import open_algorithm_selection

def open_data_MNAR(parent, root):
    parent.withdraw()
    data_MNAR = tk.Toplevel(parent)
    data_MNAR.title("MNAR Data Configuration")
    data_MNAR.geometry("600x600")  # Adjusted size
    data_MNAR.configure(bg='#F5E0C8')
    
    # Function to handle window closing
    def on_close():
        data_MNAR.destroy()
        parent.destroy()
        root.destroy()
    
    data_MNAR.protocol("WM_DELETE_WINDOW", on_close)
    
    # Main container frame
    main_frame = tk.Frame(data_MNAR, bg='#F5E0C8')
    main_frame.pack(fill="both", expand=True, padx=30, pady=30)
    
    # Title
    tk.Label(main_frame, text="MNAR Data Configuration", 
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
    
    # MNAR Parameters
    mnar_frame = tk.LabelFrame(main_frame, text="MNAR Parameters", bg='#F5E0C8', 
                             font=("Arial", 12), padx=10, pady=10)
    mnar_frame.pack(fill="x", pady=10)
    
    # Create MNAR parameter rows
    column_var = create_param_row(mnar_frame, "Column:", "col_1", 
                                "Example: col_1 (column to apply MNAR to)", 0)
    cutoff_var = create_param_row(mnar_frame, "Cutoff Value:", "0.5", 
                                "Example: 0.5 (median value)", 2)
    pi_high_var = create_param_row(mnar_frame, "Pi High:", "0.8", 
                                  "Example: 0.8 (80% missing when value ≥ cutoff)", 4)
    pi_low_var = create_param_row(mnar_frame, "Pi Low:", "0.2", 
                                "Example: 0.2 (20% missing when value < cutoff)", 6)
    
    # Button frame
    button_frame = tk.Frame(main_frame, bg='#F5E0C8')
    button_frame.pack(pady=20)
    
    # Function to execute commands
    def execute_commands():
        try:
            # Get parameters
            rows = int(rows_var.get())
            cols = int(cols_var.get())
            column = column_var.get()
            cutoff = float(cutoff_var.get())
            pi_high = float(pi_high_var.get())
            pi_low = float(pi_low_var.get())
            
            if rows <= 0 or cols <= 0:
                raise ValueError("Rows and columns must be positive integers")
            
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
            
            # Apply MNAR rule
            mnar_script = "erase_generator_MNAR_GPU.py"
            if not os.path.exists(mnar_script):
                mnar_script = os.path.join(os.path.dirname(__file__), mnar_script)
            
            mnar_cmd = [
                sys.executable, mnar_script,
                "--input", "complete_dataset.csv",
                "--column", column,
                "--cutoff", str(cutoff),
                "--pi_high", str(pi_high),
                "--pi_low", str(pi_low),
                "--output", "MNAR_dataset.csv",
                "--gpu"
            ]
            
            # Run MNAR process
            result = subprocess.run(mnar_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                messagebox.showinfo("Success", "MNAR dataset created successfully!")
            else:
                messagebox.showerror("Error", f"MNAR process failed:\n{result.stderr}")
            
            open_algorithm_selection(data_MNAR, root, "MNAR_dataset.csv")

        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            generate_btn.config(state="normal")
            data_MNAR.config(cursor="")
    
    # Function to start processing
    def start_processing():
        generate_btn.config(state="disabled")
        data_MNAR.config(cursor="watch")
        threading.Thread(target=execute_commands, daemon=True).start()
    
    # Generate button
    generate_btn = tk.Button(button_frame, text="Generate MNAR Dataset", 
                            command=start_processing, bg='#E6B7A9', 
                            font=("Arial", 12, "bold"), width=20)
    generate_btn.pack(side=tk.LEFT, padx=10)
    
    # Back button
    back_btn = tk.Button(button_frame, text="Back", command=on_close, 
                        bg='#E6B7A9', font=("Arial", 12, "bold"))
    back_btn.pack(side=tk.LEFT, padx=10)