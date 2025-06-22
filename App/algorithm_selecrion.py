from tkinter import *
import tkinter as tk
from tkinter import ttk
import pandas as pd
import numpy as np
import time
import subprocess
import os
import tempfile
import random
import sys
import importlib.util
from io import StringIO
from results import open_results_screen  # Import the next window

def calculate_score(erased_path, cleaned_path, constraints):
    """Calculate and print the quality score for a cleaned dataset."""
    try:
        erased = pd.read_csv(erased_path, na_values=['', 'NA'])
        cleaned = pd.read_csv(cleaned_path, na_values=['', 'NA'])
    except Exception as e:
        print(f"Error reading datasets: {str(e)}")
        return 0

    erased_rows, erased_cols = erased.shape
    cleaned_rows, cleaned_cols = cleaned.shape
    erased_missing = erased.isna().sum().sum()
    cleaned_missing = cleaned.isna().sum().sum()

    # Constraint values
    min_rows = constraints.get('min_rows', 0)
    min_percent = constraints.get('min_percent', 0.0)
    max_missing = constraints.get('max_missing', 0)
    col_threshold = constraints.get('col_threshold', 0)
    col_relative_threshold = constraints.get('col_relative_threshold', 0.0)
    important_cols = constraints.get('important_cols', '').split(',') if constraints.get('important_cols') else []

    # Calculate constraint adherence
    met = total = 0
    if min_rows > 0:
        total += 1
        if cleaned_rows >= min_rows: met += 1
    if min_percent > 0:
        total += 1
        if (cleaned_rows / erased_rows) * 100 >= min_percent: met += 1
    if max_missing > 0:
        total += 1
        if cleaned_missing <= max_missing: met += 1
    if col_threshold > 0:
        total += 1
        if cleaned_cols >= col_threshold: met += 1
    if col_relative_threshold > 0:
        total += 1
        if (cleaned_cols / erased_cols) * 100 >= col_relative_threshold: met += 1
    constraint_score = (met / total * 40.0) if total > 0 else 40.0

    # Missing value reduction
    if erased_missing == 0:
        missing_score = 30.0
    else:
        reduction = (erased_missing - cleaned_missing) / erased_missing
        missing_score = max(0.0, min(30.0, reduction * 30.0))

    # Data retention
    row_ret = cleaned_rows / erased_rows
    col_ret = cleaned_cols / erased_cols
    retention_score = (row_ret + col_ret) * 10.0

    # Important columns bonus
    bonus = 10.0
    if important_cols:
        # Simplified bonus calculation
        imp_retention = min(1.0, cleaned_cols / max(1, len(important_cols)))
        bonus = imp_retention * 10.0

    total_score = constraint_score + missing_score + retention_score + bonus
    return min(100, max(0, total_score))
def run_algorithm(algo_name, input_path, params):
    """Run an algorithm and return the cleaned dataset path and metrics"""
    # Convert parameters to proper types
    try:
        min_rows = int(params.get('min_rows', '0') or 0)
        min_cols = int(params.get('min_cols', '0') or 0)
        max_missing = int(params.get('max_missing', '0') or 0)
        weight = float(params.get('weight', '1.0') or 1.0)
        important_cols = [col.strip() for col in params.get('important_cols', '').split(',') if col.strip()]
        
    except ValueError:
        # Use defaults if conversion fails
        min_rows = 0
        min_cols = 0
        max_missing = 0
        weight = 1.0
        important_cols = []


    # Create constraints dictionary with proper types
    constraints = {
        'min_rows': min_rows,
        'min_percent': 0.0,  # Not in UI, default to 0
        'max_missing': max_missing,
        'col_threshold': min_cols,
        'col_relative_threshold': 0.0,  # Not in UI, default to 0
        'important_cols': ",".join(important_cols)  # Convert back to comma-separated string
    }

    # Create temp file for cleaned dataset
    temp_file = tempfile.NamedTemporaryFile(suffix=".csv", delete=False).name
    
    # Simulate different algorithm behaviors
    try:
        df = pd.read_csv(input_path)
    except Exception as e:
        print(f"Error reading input file: {str(e)}")
        return {
            "path": "",
            "cost": 100.0,
            "score": 0.0,
            "time": "0.0s",
            "rows": 0,
            "missing": 0
        }
    
    original_rows, original_cols = df.shape
    original_missing = df.isna().sum().sum()
    
    # Algorithm-specific cleaning simulation
    if "v0.0" in algo_name:
        # Basic row removal - drop rows with >30% missing
        threshold = 0.3
        df_cleaned = df.dropna(thresh=int(df.shape[1] * (1 - threshold)))
    elif "v0.1" in algo_name:
        # Iterative removal - drop rows with >30% missing
        df_cleaned = df.dropna(thresh=int(df.shape[1] * 0.7))
        # Ensure min rows constraint
        if min_rows > 0 and len(df_cleaned) < min_rows:
            # Keep top min_rows rows with least missing values
            missing_per_row = df.isna().sum(axis=1)
            sorted_indices = missing_per_row.sort_values().index[:min_rows]
            df_cleaned = df.loc[sorted_indices]  # FIX: Use loc for row selection
    elif "v0.2" in algo_name:
        # Percentile-based
        missing_per_row = df.isna().sum(axis=1)
        threshold = missing_per_row.quantile(0.75)
        df_cleaned = df[missing_per_row <= threshold]
    elif "v0.3" in algo_name:
        # Combined scoring
        missing_per_row = df.isna().sum(axis=1)
        rank = missing_per_row.rank(pct=True)
        combined = missing_per_row + rank * missing_per_row.max()
        threshold = combined.quantile(0.7)
        df_cleaned = df[combined <= threshold]
    elif "v0.4" in algo_name:
        # Optimized vectorized
        missing_per_row = df.isna().sum(axis=1)
        df_cleaned = df[missing_per_row <= missing_per_row.mean() * 1.2]
    elif "v0.5" in algo_name:
        # Constraint-driven
        if min_rows > 0:
            # Keep min_rows rows with least missing values
            missing_per_row = df.isna().sum(axis=1)
            sorted_indices = missing_per_row.sort_values().index[:min_rows]
            df_cleaned = df.loc[sorted_indices]  # FIX: Use loc for row selection
        else:
            # Random 80% sample
            df_cleaned = df.sample(frac=0.8)
    else:  # Branch & Bound
        # Optimal solution simulation
        # Drop columns with >50% missing
        missing_per_col = df.isna().mean()
        cols_to_keep = missing_per_col[missing_per_col <= 0.5].index
        df_cleaned = df[cols_to_keep]
        
        # Drop rows with >30% missing
        missing_per_row = df_cleaned.isna().sum(axis=1)
        df_cleaned = df_cleaned[missing_per_row <= df_cleaned.shape[1] * 0.3]
        
        # Ensure min rows constraint
        if min_rows > 0 and len(df_cleaned) < min_rows:
            # Keep top min_rows rows with least missing values
            missing_per_row = df.isna().sum(axis=1)
            sorted_indices = missing_per_row.sort_values().index[:min_rows]
            df_cleaned = df.loc[sorted_indices]  # FIX: Use loc for row selection
    
    # Save cleaned dataset
    try:
        df_cleaned.to_csv(temp_file, index=False)
    except Exception as e:
        print(f"Error saving cleaned data: {str(e)}")
        return {
            "path": "",
            "cost": 100.0,
            "score": 0.0,
            "time": "0.0s",
            "rows": 0,
            "missing": 0
        }
    
    # Calculate metrics
    cleaned_rows, cleaned_cols = df_cleaned.shape
    cleaned_missing = df_cleaned.isna().sum().sum()
    
    # Calculate score using our function
    try:
        score = calculate_score(
            erased_path=input_path,
            cleaned_path=temp_file,
            constraints=constraints
        )
    except Exception as e:
        print(f"Error calculating score: {str(e)}")
        score = 0.0
    
    # Return metrics
    return {
        "path": temp_file,
        "cost": round(100 - score, 1),  # Invert score to cost (lower is better)
        "score": round(score, 1),
        "time": f"{random.uniform(0.5, 5.0):.1f}s",
        "rows": cleaned_rows,
        "missing": cleaned_missing
    }


def open_algorithm_selection(data_input, root, path):
    data_input.withdraw()
    algorithm_window = Toplevel(data_input)
    algorithm_window.title("Algorithm Selection")
    algorithm_window.geometry("1000x700")
    algorithm_window.configure(bg='#F5E0C8')

    # Title label
    title_label = Label(
        algorithm_window,
        text="Algorithm Parameters",
        font=("Arial", 20, "bold"),
        bg='#E6B7A9',
        height=2,
        width=50,
        bd=3,
        relief=RAISED
    )
    title_label.pack(pady=(20, 20))

    # Path display
    path_frame = Frame(algorithm_window, bg='#F5E0C8')
    path_frame.pack(pady=(0, 15))
    Label(
        path_frame,
        text="Selected Dataset:",
        font=("Arial", 12, "bold"),
        bg='#F5E0C8'
    ).pack(side=LEFT, padx=(0, 10))
    path_label = Label(
        path_frame,
        text=path,
        font=("Arial", 12),
        bg='#D8A8C0',
        width=70,
        bd=2,
        relief=SUNKEN,
        padx=5,
        pady=2
    )
    path_label.pack(side=LEFT)

    # Parameters frame
    params_frame = Frame(algorithm_window, bg='#F5E0C8')
    params_frame.pack(pady=20, padx=50, fill=BOTH, expand=True)

    # Parameter fields
    params = [
        ("Min Rows:", "min_rows", "0"),
        ("Min Columns:", "min_cols", "0"),
        ("Max Missing:", "max_missing", "0"),
        ("Important Columns:", "important_cols", "col1,col2"),
        ("Importance Weight:", "weight", "1.0")
    ]

    entries = {}
    for i, (label, name, default) in enumerate(params):
        frame = Frame(params_frame, bg='#F5E0C8')
        frame.pack(fill=X, pady=5)
        
        Label(
            frame,
            text=label,
            font=("Arial", 12),
            bg='#F5E0C8',
            width=20,
            anchor='w'
        ).pack(side=LEFT, padx=(0, 10))
        
        entry = Entry(
            frame,
            font=("Arial", 12),
            bg='#FFFFFF',
            bd=2,
            relief=SUNKEN,
            width=30
        )
        entry.insert(0, default)
        entry.pack(side=LEFT, fill=X, expand=True)
        entries[name] = entry

    # Algorithm selection frame
    algo_selection_frame = Frame(params_frame, bg='#F5E0C8')
    algo_selection_frame.pack(fill=BOTH, expand=True, pady=10)
    
    # Algorithm selection label
    Label(
        algo_selection_frame,
        text="Select Algorithms:",
        font=("Arial", 12, "bold"),
        bg='#F5E0C8',
        anchor='w'
    ).pack(anchor='w', pady=(0, 10))
    
    # Algorithms with descriptions
    algorithms = [
        ("Algorithm v0.0", "Basic row removal based on missing counts"),
        ("Algorithm v0.1", "Iterative row removal with constraints"),
        ("Algorithm v0.2", "Percentile-based filtering with weighting"),
        ("Algorithm v0.3", "Combined scoring with constraints"),
        ("Algorithm v0.4", "Optimized with vectorized operations"),
        ("Algorithm v0.5", "Constraint-driven with prioritization"),
        ("Branch & Bound", "Optimal solution with branch and bound")
    ]
    
    algo_vars = {}
    for i, (algo, desc) in enumerate(algorithms):
        frame = Frame(algo_selection_frame, bg='#F5E0C8')
        frame.pack(fill=X, pady=3)
        
        var = IntVar(value=1)
        Checkbutton(
            frame,
            text=algo,
            variable=var,
            font=("Arial", 12),
            bg='#F5E0C8',
            anchor='w'
        ).pack(side=LEFT, padx=(0, 10))
        
        Label(
            frame,
            text=desc,
            font=("Arial", 10),
            bg='#F5E0C8',
            fg='#555555',
            anchor='w'
        ).pack(side=LEFT, fill=X, expand=True)
        
        algo_vars[algo] = var

    # Progress bar
    progress_frame = Frame(algorithm_window, bg='#F5E0C8')
    progress_frame.pack(fill=X, padx=50, pady=10)
    
    progress_label = Label(
        progress_frame,
        text="Ready to start processing",
        font=("Arial", 10),
        bg='#F5E0C8',
        anchor='w'
    )
    progress_label.pack(fill=X)
    
    progress = ttk.Progressbar(
        progress_frame,
        orient=HORIZONTAL,
        length=400,
        mode='determinate'
    )
    progress.pack(fill=X, pady=5)
    progress["value"] = 0

    # Start button
    def start_processing():
        # Collect parameters
        params = {name: entry.get() for name, entry in entries.items()}
        selected_algos = [algo for algo, var in algo_vars.items() if var.get() == 1]
        
        if not selected_algos:
            progress_label.config(text="Please select at least one algorithm")
            return
            
        # Disable button during processing
        start_btn.config(state=DISABLED)
        progress_label.config(text="Starting processing...")
        algorithm_window.update()
        
        # Process each algorithm
        results = {}
        total_algos = len(selected_algos)
        
        for i, algo in enumerate(selected_algos):
            progress_label.config(text=f"Running {algo} ({i+1}/{total_algos})...")
            progress["value"] = (i / total_algos) * 100
            algorithm_window.update()
            
            # Run algorithm (simulated)
            algo_result = run_algorithm(algo, path, params)
            results[algo] = {
                "path": algo_result["path"],
                "cost": algo_result["cost"],
                "score": algo_result["score"],
                "time": algo_result["time"],
                "rows": algo_result["rows"],
                "missing": algo_result["missing"]
            }
            
            progress["value"] = ((i+1) / total_algos) * 100
            algorithm_window.update()
            time.sleep(0.5)  # Simulate processing time
        
        progress_label.config(text="Processing complete!")
        start_btn.config(state=NORMAL)
        
        # Open results screen
        open_results_screen(algorithm_window, root, results, path)

    start_btn = Button(
        algorithm_window,
        text="Start Processing",
        command=start_processing,
        font=("Arial", 14, "bold"),
        bg='#4CAF50',
        fg='white',
        bd=3,
        relief=RAISED,
        padx=20,
        pady=10,
        cursor="hand2"
    )
    start_btn.pack(pady=20)

    # Back button
    def back_to_data_input():
        algorithm_window.destroy()
        data_input.deiconify()

    Button(
        algorithm_window,
        text="Back",
        command=back_to_data_input,
        font=("Arial", 10),
        bg='#E6B7A9',
        bd=2,
        relief=RAISED,
        padx=10,
        pady=5,
        cursor="hand2"
    ).pack(pady=10)

    # Close handling
    def on_close():
        root.destroy()
        data_input.destroy()
        algorithm_window.destroy()

    algorithm_window.protocol("WM_DELETE_WINDOW", on_close)
    