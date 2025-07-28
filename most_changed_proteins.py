import openpyxl
from openpyxl import Workbook
import tkinter as tk
from tkinter import filedialog, simpledialog
import os
import statistics

def main():
    # Initialize GUI root
    root = tk.Tk()
    root.withdraw()

    # Prompt user to select an Excel file
    file_path = filedialog.askopenfilename(
        title="Select Excel file",
        filetypes=[("Excel files", "*.xlsx *.xls")]
    )
    if not file_path:
        print("No file selected.")
        return

    # Ask user for minimum SpC and TIC thresholds
    try:
        min_spc = float(simpledialog.askstring("Minimum SpC", "Enter minimum SpC value:"))
        min_tic = float(simpledialog.askstring("Minimum TIC", "Enter minimum TIC value:"))
    except (TypeError, ValueError):
        print("Invalid threshold input.")
        return

    # Ask for output filename for the filtered list
    output_filename = simpledialog.askstring("Output File Name", "Enter filename for significantly changed proteins (without extension):")
    if not output_filename:
        print("No output filename provided.")
        return
    output_txt_file = f"{output_filename}.txt"

    # Load the workbook and find the 'Protein list' sheet
    wb = openpyxl.load_workbook(file_path)
    if "Protein list" not in wb.sheetnames:
        print("Sheet 'Protein list' not found.")
        return

    sheet = wb["Protein list"]

    # Identify headers
    headers = [cell.value for cell in sheet[1]]
    try:
        protein_col = headers.index("ProteinAC")
    except ValueError:
        try:
            protein_col = headers.index("Protein AC")
        except ValueError:
            print("Column 'ProteinAC' or 'Protein AC' not found.")
            return

    spc_cols = [i for i, h in enumerate(headers) if isinstance(h, str) and h.startswith("SpC")]
    tic_cols = [i for i, h in enumerate(headers) if isinstance(h, str) and h.startswith("TIC")]

    if not spc_cols and not tic_cols:
        print("No 'SpC' or 'TIC' columns found.")
        return

    # Build data matrix and track significantly changed proteins
    data_matrix = []
    most_changed_proteins = []

    for row in sheet.iter_rows(min_row=2, values_only=True):
        protein_ac = row[protein_col]
        if not protein_ac:
            continue

        spc_vals = [row[i] for i in spc_cols if isinstance(row[i], (int, float))]
        tic_vals = [row[i] for i in tic_cols if isinstance(row[i], (int, float))]

        avg_spc = round(statistics.mean(spc_vals), 2) if spc_vals else 0.0
        avg_tic = round(statistics.mean(tic_vals), 2) if tic_vals else 0.0

        data_matrix.append([protein_ac, avg_spc, avg_tic])

        if avg_spc >= min_spc and avg_tic >= min_tic:
            most_changed_proteins.append(protein_ac)

    # Write Summary sheet
    if "Summary" in wb.sheetnames:
        del wb["Summary"]
    summary_sheet = wb.create_sheet("Summary")
    summary_sheet.append(["Protein AC", "Average SpC", "Average TIC"])
    for row in data_matrix:
        summary_sheet.append(row)
    wb.save(file_path)

    # Write significantly changed proteins to text file
    with open(output_txt_file, "w") as f:
        for protein in most_changed_proteins:
            f.write(protein + "\n")

    print(f"\nSummary written to 'Summary' sheet in {os.path.basename(file_path)}")
    print(f"Significantly changed proteins saved to {output_txt_file}")

if __name__ == "__main__":
    main()
