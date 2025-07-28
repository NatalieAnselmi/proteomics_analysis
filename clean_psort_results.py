import tkinter as tk
from tkinter import filedialog
import re

# Hide the root window
root = tk.Tk()
root.withdraw()

# Ask the user to select the input file
input_path = filedialog.askopenfilename(title="Select the input file to read from")
if not input_path:
    print("No input file selected. Exiting...")
    exit()

# Ask the user to select the output file (or specify a new file)
output_path = filedialog.asksaveasfilename(title="Select where to save the output file", defaultextension=".txt", filetypes=[("Text files", "*.txt")])
if not output_path:
    print("No output file selected. Exiting...")
    exit()

try:
    with open(input_path, 'r') as infile, open(output_path, 'w') as outfile:
        lines = infile.readlines()
        
        # Initialize a flag to indicate when we've found "Final Prediction:"
        seqid_found = None
        final_prediction_found = None
        
        for i in range(len(lines)):
            line = lines[i]
            
            # 1. Check if the current line contains "SeqID: "
            if 'SeqID:' in line:
                # Remove 'SeqID: ' from the line and store the content
                seqid_found = line.split('SeqID: ')[-1].strip()
            
            # 2. Check if the current line contains "Final Prediction:"
            if 'Final Prediction:' in line:
                # Ensure there's a next line
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    # Remove numbers from the line after "Final Prediction:"
                    next_line_without_numbers = re.sub(r'\d+', '', next_line).strip()
                    final_prediction_found = next_line_without_numbers
            
            # If both SeqID and Final Prediction were found, write them to the output
            if seqid_found and final_prediction_found:
                # Write to the output as a two-column format
                outfile.write(f"{seqid_found}\t{final_prediction_found}\n")
                # Reset the variables for the next pair
                seqid_found = None
                final_prediction_found = None
        
    print(f"Relevant lines were written to {output_path}")
    
except FileNotFoundError:
    print("The input file was not found.")
except Exception as e:
    print("An error occurred:", e)
