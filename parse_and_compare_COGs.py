import openpyxl
import tkinter as tk
from tkinter import filedialog, messagebox
import os

# -------------------------
# COG code to category name mapping
# -------------------------
COG_CATEGORIES = {
    "A": "RNA processing and modification", "B": "Chromatin structure and dynamics",
    "C": "Energy production and conversion", "D": "Cell cycle control, cell division, chromosome partitioning",
    "E": "Amino acid transport and metabolism", "F": "Nucleotide transport and metabolism",
    "G": "Carbohydrate transport and metabolism", "H": "Coenzyme transport and metabolism",
    "I": "Lipid transport and metabolism", "J": "Translation, ribosomal structure and biogenesis",
    "K": "Transcription", "L": "Replication, recombination and repair",
    "M": "Cell wall/membrane/envelope biogenesis", "N": "Cell motility",
    "O": "Posttranslational modification, protein turnover, chaperones",
    "P": "Inorganic ion transport and metabolism", "Q": "Secondary metabolites biosynthesis, transport and catabolism",
    "R": "General function prediction only", "S": "Function unknown",
    "T": "Signal transduction mechanisms", "U": "Intracellular trafficking, secretion, and vesicular transport",
    "V": "Defense mechanisms", "W": "Extracellular structures",
    "X": "Mobilome: prophages, transposons", "Y": "Nuclear structure",
    "Z": "Cytoskeleton", "-": "Not assigned / No COG code"
}

# -------------------------
# Create_COG_lists
# -------------------------
def create_cog_lists(excel_path):
    wb = openpyxl.load_workbook(excel_path)
    sheet = wb.active

    cog_map = {}
    for row in sheet.iter_rows(min_row=4, values_only=True):
        protein_id = row[0]
        raw_cog = row[6]
        if not protein_id or str(protein_id).startswith("#"):
            continue
        if not raw_cog or raw_cog.strip() == "":
            cog_codes = ["-"]
        else:
            cog_codes = list(raw_cog.strip())
        for code in cog_codes:
            cog_map.setdefault(code, []).append(protein_id)

    base_name = os.path.splitext(os.path.basename(excel_path))[0]
    output_file = f"{base_name}_proteins_per_COG.txt"
    with open(output_file, "w") as out:
        for code in sorted(cog_map.keys()):
            proteins = cog_map[code]
            description = COG_CATEGORIES.get(code, "Unknown category")
            out.write(f"{code} – {description} ({len(proteins)})\n")
            out.write(", ".join(proteins) + "\n\n")
    return output_file

# -------------------------
# Compare_COGs helpers
# -------------------------
def parse_file(file_path):
    cog_dict = {}
    with open(file_path, 'r') as f:
        lines = f.read().splitlines()
    current_code, current_title = None, None
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if '–' in line:
            parts = line.split('–')
            if len(parts) == 2:
                current_code = parts[0].strip()
                title_part = parts[1].strip()
                current_title = title_part.split('(')[0].strip()
                cog_dict[current_code] = {"title": current_title, "proteins": []}
        elif current_code:
            proteins = [p.strip() for p in line.split(',') if p.strip()]
            cog_dict[current_code]["proteins"].extend(proteins)
    return cog_dict

def compare_multiple_cogs(file_data_list, file_titles):
    results = []
    all_codes = sorted(set().union(*(fd.keys() for fd in file_data_list)))
    for code in all_codes:
        present_files = [i for i, fd in enumerate(file_data_list) if code in fd]
        if not present_files:
            continue
        title = None
        all_sets = []
        for i in present_files:
            cog_info = file_data_list[i].get(code, {})
            title = cog_info.get("title", title)
            proteins = set(cog_info.get("proteins", []))
            all_sets.append(proteins)
        results.append(f"{code}: {title}")
        for i, proteins in enumerate(all_sets):
            others = set().union(*(s for j, s in enumerate(all_sets) if j != i))
            unique = proteins - others
            results.append(f"Unique to {file_titles[present_files[i]]}:")
            results.append(', '.join(sorted(unique)) if unique else "(none)")
        results.append("")
    return results

def process_files(file_paths, output_path):
    file_data_list = [parse_file(p) for p in file_paths]
    file_titles = [os.path.basename(p) for p in file_paths]
    results = compare_multiple_cogs(file_data_list, file_titles)
    with open(output_path, "w") as f:
        f.write("\n".join(results))

# -------------------------
# GUI pipeline
# -------------------------
def launch_gui():
    root = tk.Tk()
    root.title("COG Pipeline")
    root.geometry("600x700")

    file_buttons = []
    selected_paths = []
    run_button = None

    # --- Single parse section (unchanged) ---
    def parse_one_file():
        excel_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
        if not excel_path:
            return
        try:
            out_file = create_cog_lists(excel_path)
            messagebox.showinfo("Done", f"Created: {out_file}")
        except Exception as e:
            messagebox.showerror("Error", f"Error parsing file:\n{e}")

    # --- Helpers for multi-file selection ---
    def check_all_selected():
        if all(selected_paths):
            run_button.pack(pady=20)
        else:
            run_button.forget()

    def browse_file(idx):
        path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
        if path:
            selected_paths[idx] = path
            file_buttons[idx].config(text=os.path.basename(path))
            check_all_selected()

    def load_file_inputs(count):
        for widget in file_input_frame.winfo_children():
            widget.destroy()
        file_buttons.clear()
        selected_paths.clear()
        for i in range(count):
            frame = tk.Frame(file_input_frame)
            frame.pack(pady=8)
            tk.Label(frame, text=f"Excel file {i+1}:").pack(side="left", padx=5)
            btn = tk.Button(frame, text="Browse", command=lambda idx=i: browse_file(idx))
            btn.pack(side="left", padx=5)
            file_buttons.append(btn)
            selected_paths.append(None)
        check_all_selected()

    def get_file_count():
        try:
            count = int(file_count_entry.get())
            if count < 2:
                raise ValueError
            load_file_inputs(count)
        except ValueError:
            messagebox.showerror("Invalid input", "Please enter an integer ≥ 2.")

    def process():
        if not all(selected_paths):
            messagebox.showerror("Error", "Please select all files.")
            return
        txt_paths = []
        try:
            for path in selected_paths:
                txt_file = create_cog_lists(path)
                txt_paths.append(txt_file)
        except Exception as e:
            messagebox.showerror("Error", f"Error in Create_COG_lists:\n{e}")
            return
        output_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if not output_path:
            return
        try:
            process_files(txt_paths, output_path)
            messagebox.showinfo("Done", f"Comparison saved to: {output_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Error in Compare_COGs:\n{e}")

    # --- Layout ---
    tk.Label(root, text="Parse just 1 file", font=("Arial", 18, "bold")).pack(pady=10)
    tk.Button(root, text="Single parse", command=parse_one_file).pack(pady=10)

    tk.Label(root, text="Full pipeline (parse & compare):", font=("Arial", 18, "bold")).pack(pady=5)
    tk.Label(root, text="How many files to parse and compare? (≥ 2)").pack(pady=5)

    file_count_entry = tk.Entry(root, justify='center')
    file_count_entry.pack()

    tk.Button(root, text="Confirm", command=get_file_count).pack(pady=5)

    file_input_frame = tk.Frame(root)
    file_input_frame.pack(pady=10)

    run_button = tk.Button(root, text="Run Pipeline", command=process, fg="red")

    root.mainloop()

if __name__ == "__main__":
    launch_gui()
