import tkinter as tk
from tkinter import filedialog

def open_file():
    # Function to ask the user for a file to open
    root = tk.Tk()
    root.withdraw()  # Hide the Tkinter root window
    file_path = filedialog.askopenfilename(title="Select the file to open")
    return file_path

def save_file():
    # Function to ask the user for a file to save the data to (create a new one if needed)
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")], title="Select the file to save to")
    return file_path

def process_and_save():
    # Function to process the matrix and save the last two columns
    file_path_1 = open_file()
    if not file_path_1:
        print("No file selected.")
        return
    
    try:
        # Read the data from doc 1 (assuming it's space or tab-separated values)
        with open(file_path_1, 'r') as file:
            lines = file.readlines()
        
        # Process the matrix to extract the last two columns
        last_two_columns = []
        for line in lines:
            columns = line.split()  # Split by any whitespace
            if len(columns) >= 2:  # Ensure there are at least two columns
                last_two_columns.append(columns[-2:])  # Get last two columns
        
        # Save the last two columns into doc 2
        file_path_2 = save_file()
        if not file_path_2:
            print("No file selected for saving.")
            return

        with open(file_path_2, 'w') as file:
            for row in last_two_columns:
                file.write("\t".join(row) + "\n")  # Join by tab and write to file

        print(f"Last two columns have been saved to {file_path_2}")

    except Exception as e:
        print(f"Error occurred: {e}")

def main():
    process_and_save()

if __name__ == "__main__":
    main()
