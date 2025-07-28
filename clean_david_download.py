import tkinter as tk
from tkinter import filedialog
import os
import sys
import pandas as pd

def strip_term(term):
    """Remove everything before and including the '~' character in a string"""
    return term.split('~')[-1] if '~' in term else term

def process_file():
    # Hide the tkinter root window
    root = tk.Tk()
    root.withdraw()

    # Ask the user to select the input file
    input_path = filedialog.askopenfilename(title="Select the input file to read from")
    if not input_path:
        print("No input file selected. Exiting...")
        sys.exit()

    try:
        with open(input_path, 'r', encoding='utf-8') as infile:
            lines = infile.readlines()

        headers = lines[0].strip().split('\t')
        required_cols = ['Term', 'Count', 'PValue', 'FDR', 'Genes']

        col_index = {col: headers.index(col) for col in required_cols if col in headers}
        if len(col_index) < len(required_cols):
            missing = [col for col in required_cols if col not in headers]
            print(f"Error: Missing required columns: {', '.join(missing)}")
            sys.exit()

        overview_data = []
        sig_data = []
        gene_list_blocks = []

        for line in lines[1:]:
            parts = line.strip().split('\t')
            if len(parts) < len(headers):
                continue  # skip malformed rows

            term_raw = parts[col_index['Term']]
            term = strip_term(term_raw)
            count = parts[col_index['Count']]
            pvalue_str = parts[col_index['PValue']]
            fdr_str = parts[col_index['FDR']]
            genes = parts[col_index['Genes']]

            try:
                pvalue = float(pvalue_str)
                fdr = float(fdr_str)
            except ValueError:
                continue  # skip rows with invalid numbers

            # Add to overview data
            overview_data.append({'Term': term, 'Count': count, 'PValue': pvalue, 'FDR': fdr})

            # Add to significant data (FDR <= 0.05)
            if fdr <= 0.05:
                sig_data.append({'Term': term, 'Count': count, 'FDR': fdr})

            # Gene list block
            gene_list_blocks.append(f"{term}\n{genes}\n")

        base_dir = os.path.dirname(input_path)
        excel_output_path = os.path.join(base_dir, 'DAVID_output.xlsx')
        gene_list_path = os.path.join(base_dir, 'DAVID_genes_output.txt')

        # Save both dataframes into one Excel file with two sheets
        with pd.ExcelWriter(excel_output_path, engine='openpyxl') as writer:
            pd.DataFrame(overview_data).to_excel(writer, index=False, sheet_name='Overview')
            pd.DataFrame(sig_data).to_excel(writer, index=False, sheet_name='Sig_Categories')

        # Write gene list text output
        with open(gene_list_path, 'w', encoding='utf-8') as out2:
            out2.write('\n'.join(gene_list_blocks))

        print("Success! Files created:")
        print(f"- {excel_output_path}")
        print(f"- {gene_list_path}")

    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit()

if __name__ == '__main__':
    process_file()
