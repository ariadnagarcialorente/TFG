import os
import re
from pathlib import Path

def extract_score_data(file_path):
    """Extract score breakdown and total score from a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Find the score breakdown section
        score_pattern = r'================ SCORE BREAKDOWN =================\n(.*?)================== TOTAL SCORE ==================='
        total_pattern = r'================== TOTAL SCORE ===================\n(.*?)(?:\n|$)'
        
        score_match = re.search(score_pattern, content, re.DOTALL)
        total_match = re.search(total_pattern, content, re.DOTALL)
        
        if score_match and total_match:
            score_section = score_match.group(1).strip()
            total_section = total_match.group(1).strip()
            
            return f"File: {file_path.name}\n" + \
                   "================ SCORE BREAKDOWN =================\n" + \
                   score_section + "\n" + \
                   "================== TOTAL SCORE ===================\n" + \
                   total_section + "\n"
        else:
            return f"File: {file_path.name}\nScore data not found in expected format.\n"
            
    except Exception as e:
        return f"File: {file_path.name}\nError reading file: {str(e)}\n"

def process_directory(directory_path, output_file=None):
    """Process all *eval.log files in a directory and extract score data."""
    directory = Path(directory_path)
    
    if not directory.exists():
        print(f"Directory {directory_path} does not exist.")
        return
    
    results = []
    
    # Get all *eval.log files and sort them by name
    eval_files = [f for f in directory.iterdir() if f.is_file() and f.name.endswith('eval.log')]
    eval_files.sort(key=lambda x: x.name)
    
    # Process files in alphabetical order
    for file_path in eval_files:
        extracted_data = extract_score_data(file_path)
        results.append(extracted_data)
        print(extracted_data)
        print("-" * 50)
    
    if not eval_files:
        print("No *eval.log files found in the directory.")
        return
    
    # Optionally save to output file
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(results))
        print(f"\nResults saved to {output_file}")

def process_single_file(file_path):
    """Process a single file and extract score data."""
    file_path = Path(file_path)
    
    if not file_path.exists():
        print(f"File {file_path} does not exist.")
        return
    
    extracted_data = extract_score_data(file_path)
    print(extracted_data)
    return extracted_data

# Example usage:
if __name__ == "__main__":
    # Process all *eval.log files in current directory
    # process_directory(".", "extracted_scores.txt")
    
    # Or process a specific directory for *eval.log files
    # process_directory("/path/to/your/files", "extracted_scores.txt")
    
    # Or process a single file
    # process_single_file("your_file.txt")
    
    # Interactive mode - ask user for input
    choice = input("Enter 'd' for directory, 'f' for single file: ").lower().strip()
    
    if choice == 'd':
        dir_path = input("Enter directory path (or '.' for current directory): ").strip()
        save_output = input("Save to file? (y/n): ").lower().strip() == 'y'
        output_file = None
        if save_output:
            output_file = input("Enter output filename (default: extracted_scores.txt): ").strip()
            if not output_file:
                output_file = "extracted_scores.txt"
        process_directory(dir_path, output_file)
    
    elif choice == 'f':
        file_path = input("Enter file path: ").strip()
        process_single_file(file_path)
    
    else:
        print("Invalid choice. Please run the script again.")