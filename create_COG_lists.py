import openpyxl
import tkinter as tk
from tkinter import filedialog
import os

# COG code to category name mapping
COG_CATEGORIES = {
    "A": "RNA processing and modification",
    "B": "Chromatin structure and dynamics",
    "C": "Energy production and conversion",
    "D": "Cell cycle control, cell division, chromosome partitioning",
    "E": "Amino acid transport and metabolism",
    "F": "Nucleotide transport and metabolism",
    "G": "Carbohydrate transport and metabolism",
    "H": "Coenzyme transport and metabolism",
    "I": "Lipid transport and metabolism",
    "J": "Translation, ribosomal structure and biogenesis",
    "K": "Transcription",
    "L": "Replication, recombination and repair",
    "M": "Cell wall/membrane/envelope biogenesis",
    "N": "Cell motility",
    "O": "Posttranslational modification, protein turnover, chaperones",
    "P": "Inorganic ion transport and metabolism",
    "Q": "Secondary metabolites biosynthesis, transport and catabolism",
    "R": "General function prediction only",
    "S": "Function unknown",
    "T": "Signal transduction mechanisms",
    "U": "Intracellular trafficking, secretion, and vesicular transport",
    "V": "Defense mechanisms",
    "W": "Extracellular structures",
    "X": "Mobilome: prophages, transposons",
    "Y": "Nuclear structure",
    "Z": "Cytoskeleton",
    "-": "Not assigned / No COG code"
}

def main():
    # Prompt user to select Excel file
    root = tk.Tk()
    root.withdraw()
    excel_path = filedialog.askopenfilename(
        title="Select Excel file",
        filetypes=[("Excel files", "*.xlsx *.xls")]
    )
    if not excel_path:
        print("No file selected.")
        return

    # Load Excel workbook and sheet
    wb = openpyxl.load_workbook(excel_path)
    sheet = wb.active

    # Dictionary to store proteins per COG code
    cog_map = {}

    # Process each row starting from row 4
    for row in sheet.iter_rows(min_row=4, values_only=True):
        protein_id = row[0]
        raw_cog = row[6]  # Column G (COG_category)

        if not protein_id:
            continue
        if str(protein_id).startswith("#"):
            continue  # Skip rows where protein_id starts with '#'

        # If no COG, treat as "-"
        if not raw_cog or raw_cog.strip() == "":
            cog_codes = ["-"]
        else:
            # Split characters individually (e.g., "CO" → ["C", "O"])
            cog_codes = list(raw_cog.strip())

        for code in cog_codes:
            if code not in cog_map:
                cog_map[code] = []
            cog_map[code].append(protein_id)

    # Prepare output file
    base_name = os.path.splitext(os.path.basename(excel_path))[0]
    output_file = f"{base_name}_proteins_per_COG.txt"

    with open(output_file, "w") as out:
        for code in sorted(cog_map.keys()):
            proteins = cog_map[code]
            description = COG_CATEGORIES.get(code, "Unknown category")
            out.write(f"{code} – {description} ({len(proteins)})\n")
            out.write(", ".join(proteins) + "\n\n")

    print(f"Output saved to: {output_file}")

if __name__ == "__main__":
    main()
