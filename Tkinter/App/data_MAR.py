import tkinter as tk
from tkinter import messagebox
import subprocess
import threading
import os
import sys

def open_data_MAR(parent, root):
    parent.withdraw()
    data_MAR = tk.Toplevel(parent)
    data_MAR.title("MAR Data Configuration")
    data_MAR.geometry("800x650")
    data_MAR.configure(bg='#F5E0C8')
    
    # Function to handle window closing
    def on_close():
        data_MAR.destroy()
        parent.destroy()
        root.destroy()
    
    data_MAR.protocol("WM_DELETE_WINDOW", on_close)
    
    # Main container frame
    main_frame = tk.Frame(data_MAR, bg='#F5E0C8')
    main_frame.pack(fill="both", expand=True, padx=30, pady=30)
    
    # Title
    tk.Label(main_frame, text="MAR Data Configuration", 
            bg='#F5E0C8', font=("Arial", 16, "bold")).pack(pady=10)
    
    # Dataset Parameters
    dataset_frame = tk.LabelFrame(main_frame, text="Dataset Parameters", bg='#F5E0C8', 
                                font=("Arial", 12), padx=10, pady=10)
    dataset_frame.pack(fill="x", pady=10)
    
    # Simple grid layout for parameters
    def create_param_row(frame, label, default, row):
        tk.Label(frame, text=label, bg='#F5E0C8', anchor="w", 
                font=("Arial", 10)).grid(row=row, column=0, padx=5, pady=5, sticky="w")
        var = tk.StringVar(value=default)
        entry = tk.Entry(frame, textvariable=var, bg='#D8A8C0', 
                        font=("Arial", 10), width=15)
        entry.grid(row=row, column=1, padx=5, pady=5, sticky="e")
        return var
    
    # Create parameter rows
    tk.Label(dataset_frame, text="Number of Rows:", bg='#F5E0C8', 
            font=("Arial", 10)).grid(row=0, column=0, padx=5, pady=5, sticky="w")
    rows_var = tk.StringVar(value="10000")
    rows_entry = tk.Entry(dataset_frame, textvariable=rows_var, bg='#D8A8C0', 
                         font=("Arial", 10), width=15)
    rows_entry.grid(row=0, column=1, padx=5, pady=5, sticky="e")
    
    tk.Label(dataset_frame, text="Number of Columns:", bg='#F5E0C8', 
            font=("Arial", 10)).grid(row=1, column=0, padx=5, pady=5, sticky="w")
    cols_var = tk.StringVar(value="20")
    cols_entry = tk.Entry(dataset_frame, textvariable=cols_var, bg='#D8A8C0', 
                         font=("Arial", 10), width=15)
    cols_entry.grid(row=1, column=1, padx=5, pady=5, sticky="e")
    
    # MAR Rules Configuration
    rules_frame = tk.LabelFrame(main_frame, text="MAR Rules Configuration", bg='#F5E0C8', 
                              font=("Arial", 12), padx=10, pady=10)
    rules_frame.pack(fill="x", pady=10)
    
    # Create rule input rows
    def create_rule_row(frame, label, example, default, row):
        # Main label
        tk.Label(frame, text=label, bg='#F5E0C8', anchor="w", 
                font=("Arial", 10)).grid(row=row, column=0, padx=5, pady=5, sticky="w")
        
        # Entry field
        var = tk.StringVar(value=default)
        entry = tk.Entry(frame, textvariable=var, bg='#D8A8C0', 
                        font=("Arial", 10), width=20)
        entry.grid(row=row, column=1, padx=5, pady=5, sticky="e")
        
        # Example text below
        example_label = tk.Label(frame, text=example, bg='#F5E0C8', anchor="w", 
                               fg="#666666", font=("Arial", 9))
        example_label.grid(row=row+1, column=0, columnspan=2, padx=5, sticky="w")
        
        return var
    
    # Create rule rows
    ref_var = create_rule_row(rules_frame, "Reference Column:", 
                             "Example: col_1", "", 0)
    tgt_var = create_rule_row(rules_frame, "Target Column:", 
                             "Example: col_2", "", 2)
    cutoff_var = create_rule_row(rules_frame, "Cutoff Value:", 
                                "Example: 0.5 (median value)", "", 4)
    pi_high_var = create_rule_row(rules_frame, "Pi High:", 
                                  "Example: 0.8 (80% missing when ref ≥ cutoff)", "0.8", 6)
    pi_low_var = create_rule_row(rules_frame, "Pi Low:", 
                                "Example: 0.2 (20% missing when ref < cutoff)", "0.2", 8)
    
    # Button frame
    button_frame = tk.Frame(main_frame, bg='#F5E0C8')
    button_frame.pack(pady=20)
    
    # Function to execute commands
    def execute_commands():
        try:
            # Get parameters
            rows = int(rows_var.get())
            cols = int(cols_var.get())
            
            if rows <= 0 or cols <= 0:
                raise ValueError("Rows and columns must be positive integers")
            
            # Get rule parameters
            rule = (
                ref_var.get(),
                tgt_var.get(),
                cutoff_var.get(),
                pi_high_var.get(),
                pi_low_var.get()
            )
            
            # Validate rule
            if not all(rule):
                raise ValueError("All MAR rule fields must be filled")
            
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
            
            # Apply MAR rule
            mar_script = "erase_generator_MAR_GPU.py"
            if not os.path.exists(mar_script):
                mar_script = os.path.join(os.path.dirname(__file__), mar_script)
            
            mar_cmd = [
                sys.executable, mar_script,
                "--input", "complete_dataset.csv",
                "--output", "MAR_dataset.csv",
                "--reference_column", rule[0],
                "--target_column", rule[1],
                "--cutoff", rule[2],
                "--pi_high", rule[3],
                "--pi_low", rule[4],
                "--gpu"
            ]
            
            # Run MAR process
            result = subprocess.run(mar_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                messagebox.showinfo("Success", "MAR dataset created successfully!")
            else:
                messagebox.showerror("Error", f"MAR process failed:\n{result.stderr}")
        
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            generate_btn.config(state="normal")
            data_MAR.config(cursor="")
    
    # Function to start processing
    def start_processing():
        generate_btn.config(state="disabled")
        data_MAR.config(cursor="watch")
        threading.Thread(target=execute_commands, daemon=True).start()
    
    # Generate button
    generate_btn = tk.Button(button_frame, text="Generate MAR Dataset", 
                            command=start_processing, bg='#E6B7A9', 
                            font=("Arial", 12, "bold"), width=20)
    generate_btn.pack(side=tk.LEFT, padx=10)
    
    # Back button
    back_btn = tk.Button(button_frame, text="Back", command=on_close, 
                        bg='#E6B7A9', font=("Arial", 12, "bold"))
    back_btn.pack(side=tk.LEFT, padx=10)
