from tkinter import *
import tkinter as tk
from tkinter import ttk

def open_results_screen(algorithm_window, root, results, input_path):
    algorithm_window.withdraw()
    results_window = Toplevel(algorithm_window)
    results_window.title("Results")
    results_window.geometry("1000x700")
    results_window.configure(bg='#F5E0C8')

    # Title label
    title_label = Label(
        results_window,
        text="Algorithm Results",
        font=("Arial", 20, "bold"),
        bg='#E6B7A9',
        height=2,
        width=50,
        bd=3,
        relief=RAISED
    )
    title_label.pack(pady=(20, 20))

    # Results table
    frame = Frame(results_window, bg='#F5E0C8')
    frame.pack(fill=BOTH, expand=True, padx=50, pady=20)
    
    # Create treeview with scrollbar
    tree = ttk.Treeview(frame, columns=("Algorithm", "Score", "Time", "Rows", "Missing"), show="headings")
    vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)
    
    # Define columns
    tree.heading("Algorithm", text="Algorithm")
    tree.heading("Score", text="Score")
    tree.heading("Time", text="Time")
    tree.heading("Rows", text="Rows Kept")
    tree.heading("Missing", text="Missing Values")
    
    tree.column("Algorithm", width=200, anchor='w')
    tree.column("Score", width=70, anchor='center')
    tree.column("Time", width=80, anchor='center')
    tree.column("Rows", width=80, anchor='center')
    tree.column("Missing", width=100, anchor='center')
    
    # Insert data
    for algo, metrics in results.items():
        tree.insert("", "end", values=(
            algo,
            metrics["score"],
            metrics["time"],
            metrics["rows"],
            metrics["missing"]
        ))
    
    # Pack widgets
    tree.pack(side=LEFT, fill=BOTH, expand=True)
    vsb.pack(side=RIGHT, fill=Y)
    
    # Best result indicator
    if results:
        best_algo = min(results, key=lambda k: results[k]["score"])
        best_frame = Frame(results_window, bg='#F5E0C8')
        best_frame.pack(pady=(10, 0))
        Label(
            best_frame,
            text="Best Performing Algorithm:",
            font=("Arial", 12, "bold"),
            bg='#F5E0C8'
        ).pack(side=LEFT, padx=(0, 10))
        Label(
            best_frame,
            text=f"{best_algo} (Score: {results[best_algo]['score']}, Score: {results[best_algo]['score']})",
            font=("Arial", 12, "bold"),
            bg='#F5E0C8',
            fg='#006400'  # Dark green
        ).pack(side=LEFT)

    # Buttons frame
    buttons_frame = Frame(results_window, bg='#F5E0C8')
    buttons_frame.pack(pady=20)

    # Back to welcome button
    def back_to_welcome():
        results_window.destroy()
        algorithm_window.destroy()
        root.deiconify()

    Button(
        buttons_frame,
        text="Back to Welcome",
        command=back_to_welcome,
        font=("Arial", 12, "bold"),
        bg='#2196F3',
        fg='white',
        bd=3,
        relief=RAISED,
        padx=15,
        pady=8,
        cursor="hand2"
    ).pack(side=LEFT, padx=20)

    # Restart button
    def restart_process():
        results_window.destroy()
        algorithm_window.destroy()
        root.deiconify()

    Button(
        buttons_frame,
        text="Run Again",
        command=restart_process,
        font=("Arial", 12, "bold"),
        bg='#FF9800',
        fg='white',
        bd=3,
        relief=RAISED,
        padx=15,
        pady=8,
        cursor="hand2"
    ).pack(side=LEFT, padx=20)
    
    # Export button
    def export_results():
        export_path = os.path.join(os.getcwd(), "cleaning_results.csv")
        with open(export_path, "w") as f:
            f.write("Algorithm,Score,Time,Rows Kept,Missing Values\n")
            for algo, metrics in results.items():
                f.write(f"{algo},{metrics['score']},{metrics['score']},{metrics['time']},{metrics['rows']},{metrics['missing']}\n")
        
        Label(
            buttons_frame,
            text=f"Exported to {export_path}",
            font=("Arial", 10),
            bg='#F5E0C8',
            fg='green'
        ).pack(side=LEFT, padx=20)
        results_window.update()

    Button(
        buttons_frame,
        text="Export Results",
        command=export_results,
        font=("Arial", 12, "bold"),
        bg='#9C27B0',
        fg='white',
        bd=3,
        relief=RAISED,
        padx=15,
        pady=8,
        cursor="hand2"
    ).pack(side=LEFT, padx=20)
    
    # Preview button
    def preview_dataset():
        preview_window = Toplevel(results_window)
        preview_window.title("Dataset Preview")
        preview_window.geometry("800x400")
        
        # Create notebook for different datasets
        notebook = ttk.Notebook(preview_window)
        notebook.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Input dataset
        input_frame = Frame(notebook)
        notebook.add(input_frame, text="Input Dataset")
        input_label = Label(input_frame, text=f"Input Dataset: {input_path}", font=("Arial", 10, "bold"))
        input_label.pack(pady=5)
        input_data = pd.read_csv(input_path)
        input_tree = ttk.Treeview(input_frame)
        input_tree["columns"] = list(input_data.columns)
        for col in input_data.columns:
            input_tree.heading(col, text=col)
            input_tree.column(col, width=100)
        for i, row in input_data.head(10).iterrows():
            input_tree.insert("", "end", values=list(row))
        scrollbar = ttk.Scrollbar(input_frame, orient="vertical", command=input_tree.yview)
        input_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        input_tree.pack(fill=BOTH, expand=True)
        
        # Add tabs for each algorithm result
        for algo, metrics in results.items():
            algo_frame = Frame(notebook)
            notebook.add(algo_frame, text=algo)
            algo_label = Label(algo_frame, text=f"Cleaned Dataset: {metrics['path']}", font=("Arial", 10, "bold"))
            algo_label.pack(pady=5)
            algo_data = pd.read_csv(metrics["path"])
            algo_tree = ttk.Treeview(algo_frame)
            algo_tree["columns"] = list(algo_data.columns)
            for col in algo_data.columns:
                algo_tree.heading(col, text=col)
                algo_tree.column(col, width=100)
            for i, row in algo_data.head(10).iterrows():
                algo_tree.insert("", "end", values=list(row))
            scrollbar = ttk.Scrollbar(algo_frame, orient="vertical", command=algo_tree.yview)
            algo_tree.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side="right", fill="y")
            algo_tree.pack(fill=BOTH, expand=True)

    Button(
        buttons_frame,
        text="Preview Datasets",
        command=preview_dataset,
        font=("Arial", 12, "bold"),
        bg='#607D8B',
        fg='white',
        bd=3,
        relief=RAISED,
        padx=15,
        pady=8,
        cursor="hand2"
    ).pack(side=LEFT, padx=20)

    # Close handling
    def on_close():
        root.destroy()
        algorithm_window.destroy()
        results_window.destroy()

    results_window.protocol("WM_DELETE_WINDOW", on_close)
    