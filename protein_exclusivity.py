import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import os

# Acceptable variations
SHEET_NAMES = ['protein list', 'protein_list']
COLUMN_NAMES = ['protein ac', 'proteins ac']

def find_protein_column(df):
    #Finds the appropriate 'Protein AC' column and allows variations like 'ProteinAC', 'protein_ac', 'Proteins AC', etc.
    for col in df.columns:
        col_clean = col.lower().replace(" ", "").replace("_", "")
        if "protein" in col_clean and "ac" in col_clean:
            return df[col].dropna().astype(str).str.strip()
    return None

def load_protein_column_from_excel(path):
    # Loads protein accession column from a target sheet in a given Excel file.
    try:
        xl = pd.ExcelFile(path)
        # Match sheet name ignoring case and underscores
        sheet_name = next((s for s in xl.sheet_names if s.strip().lower().replace('_', ' ') in SHEET_NAMES), None)
        if not sheet_name:
            raise ValueError("No matching sheet found.")
        df = xl.parse(sheet_name)
        col = find_protein_column(df)
        if col is None:
            raise ValueError("No matching 'Protein AC' column found.")
        return set(col)
    except Exception as e:
        raise ValueError(f"{os.path.basename(path)}: {e}")

def compare_protein_sets(file_paths):
    # Compares sets of protein accessions and identifies shared and unique entries.
    protein_sets = []
    filenames = [os.path.basename(p) for p in file_paths]

    for path in file_paths:
        proteins = load_protein_column_from_excel(path)
        protein_sets.append(proteins)

    # Find shared proteins
    shared = set.intersection(*protein_sets)

    # Find unique proteins for each file
    unique_lists = []
    for i, protein_set in enumerate(protein_sets):
        others = set.union(*(s for j, s in enumerate(protein_sets) if j != i))
        unique = protein_set - others
        unique_lists.append(unique)

    # Create DataFrame to export
    all_lengths = [len(shared)] + [len(u) for u in unique_lists]
    max_len = max(all_lengths)

    data = {}
    for fname, unique in zip(filenames, unique_lists):
        padded = list(unique) + [''] * (max_len - len(unique))
        data[f"Unique to {fname}"] = padded

    shared_list = list(shared) + [''] * (max_len - len(shared))
    data["Shared Proteins"] = shared_list

    df_out = pd.DataFrame(data)
    df_out.to_excel("Protein_exclusivity.xlsx", index=False)

def launch_gui():
    root = tk.Tk()
    root.title("Protein AC Excel Comparator")
    root.geometry("600x700")

    file_labels = []

    def get_file_count():
        try:
            count = int(file_count_entry.get())
            if count < 2:
                raise ValueError
            load_file_inputs(count)
        except ValueError:
            messagebox.showerror("Invalid input", "Please enter an integer ≥ 2.")

    def load_file_inputs(count):
        for widget in file_input_frame.winfo_children():
            widget.destroy()
        file_labels.clear()

        for i in range(count):
            frame = tk.Frame(file_input_frame)
            frame.pack(pady=8)
            tk.Label(frame, text=f"Select file {i + 1}", anchor='center', justify='center').pack()
            label = tk.Label(frame, text="", wraplength=550, justify='center')
            label.pack()
            tk.Button(frame, text="Browse", command=lambda lbl=label: browse_file(lbl)).pack(pady=2)
            file_labels.append(label)

    def browse_file(label):
        path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
        if path:
            label.config(text=path)

    def process():
        file_paths = [lbl.cget("text") for lbl in file_labels]
        if not all(file_paths):
            messagebox.showerror("Error", "Please select all files.")
            return
        try:
            compare_protein_sets(file_paths)
            messagebox.showinfo("Done", "Protein_exclusivity.xlsx created successfully.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # Input for number of files
    tk.Label(root, text="How many Excel files do you want to compare? (≥ 2)", justify="center").pack(pady=10)
    file_count_entry = tk.Entry(root, justify='center')
    file_count_entry.pack()
    tk.Button(root, text="Confirm", command=get_file_count).pack(pady=5)

    # File input area
    file_input_frame = tk.Frame(root)
    file_input_frame.pack(pady=10)

    # Run comparison
    tk.Button(root, text="Compare Files", command=process, bg='green', fg='white').pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    launch_gui()
