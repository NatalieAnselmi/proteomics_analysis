import tkinter as tk
from tkinter import filedialog, messagebox
import re, os, sys
import pandas as pd

def launch_gui():
    root = tk.Tk()
    root.title("Cleaner")
    root.geometry("600x650")

    container = tk.Frame(root)
    container.pack(expand=True, padx=20, pady=20)

    # -----------------------------
    # Cleaning functions (unchanged)
    # -----------------------------
    def clean_psortb(files):
        for input_path in files:
            try:
                output_path = os.path.splitext(input_path)[0] + "_cleaned.txt"
                with open(input_path, 'r') as infile, open(output_path, 'w') as outfile:
                    lines = infile.readlines()
                    seqid_found, final_prediction_found = None, None
                    for i, line in enumerate(lines):
                        if 'SeqID:' in line:
                            seqid_found = line.split('SeqID: ')[-1].strip()
                        if 'Final Prediction:' in line and i + 1 < len(lines):
                            next_line = re.sub(r'\d+', '', lines[i + 1].strip()).strip()
                            final_prediction_found = next_line
                        if seqid_found and final_prediction_found:
                            outfile.write(f"{seqid_found}\t{final_prediction_found}\n")
                            seqid_found, final_prediction_found = None, None
                print(f"psortb cleaned: {output_path}")
            except Exception as e:
                print(f"Error cleaning psortb file {input_path}: {e}")

    def clean_cello(files):
        for input_path in files:
            try:
                with open(input_path, 'r') as infile:
                    lines = infile.readlines()
                last_two_columns = [line.split()[-2:] for line in lines if len(line.split()) >= 2]
                output_path = os.path.splitext(input_path)[0] + "_cleaned.txt"
                with open(output_path, 'w') as outfile:
                    for row in last_two_columns:
                        outfile.write("\t".join(row) + "\n")
                print(f"CELLO cleaned: {output_path}")
            except Exception as e:
                print(f"Error cleaning CELLO file {input_path}: {e}")

    def strip_term(term): return re.sub(r'~.*', '', term).strip()

    def clean_david(files):
        for input_path in files:
            try:
                with open(input_path, 'r', encoding='utf-8') as infile:
                    lines = infile.readlines()
                headers = lines[0].strip().split('\t')
                required = ['Term','Count','PValue','FDR','Genes']
                col_index = {c: headers.index(c) for c in required if c in headers}
                if len(col_index) < len(required):
                    missing = [c for c in required if c not in headers]
                    print(f"Error: Missing {missing} in {input_path}")
                    continue
                overview, sig, gene_blocks = [], [], []
                for line in lines[1:]:
                    parts = line.strip().split('\t')
                    if len(parts) < len(headers): continue
                    term = strip_term(parts[col_index['Term']])
                    count = parts[col_index['Count']]
                    try:
                        pval, fdr = float(parts[col_index['PValue']]), float(parts[col_index['FDR']])
                    except ValueError: continue
                    genes = parts[col_index['Genes']]
                    overview.append({'Term':term,'Count':count,'PValue':pval,'FDR':fdr})
                    if fdr <= 0.05: sig.append({'Term':term,'Count':count,'FDR':fdr})
                    gene_blocks.append(f"{term}\n{genes}\n")
                base = os.path.splitext(input_path)[0]
                excel_out, genes_out = base+"_cleaned.xlsx", base+"_genes_cleaned.txt"
                with pd.ExcelWriter(excel_out, engine="openpyxl") as w:
                    pd.DataFrame(overview).to_excel(w,index=False,sheet_name="Overview")
                    pd.DataFrame(sig).to_excel(w,index=False,sheet_name="Sig_Categories")
                with open(genes_out,"w",encoding="utf-8") as g: g.write("\n".join(gene_blocks))
                print(f"DAVID cleaned: {excel_out}, {genes_out}")
            except Exception as e: print(f"Error cleaning DAVID file {input_path}: {e}")

    def clean_fasta_metadata(files):
        for input_path in files:
            try:
                output_path = os.path.splitext(input_path)[0] + "_cleaned.fasta"
                with open(input_path,'r') as infile, open(output_path,'w') as outfile:
                    entry_id, seq, in_seq = None, [], False
                    for line in infile:
                        line=line.strip()
                        if line.startswith("ID"):
                            if entry_id and seq:
                                outfile.write(f">{entry_id}\n{''.join(seq)}\n")
                            entry_id=line.split()[1].split("_")[0]
                            seq,in_seq=[],False
                        elif line.startswith("SQ"): in_seq=True
                        elif line.startswith("//"):
                            if entry_id and seq:
                                outfile.write(f">{entry_id}\n{''.join(seq)}\n")
                            entry_id,seq,in_seq=None,[],False
                        elif in_seq: seq.append("".join(filter(str.isalpha,line)))
                print(f"FASTA cleaned: {output_path}")
            except Exception as e: print(f"Error cleaning FASTA file {input_path}: {e}")

    tool_cleaners = {"psortb":clean_psortb,"CELLO":clean_cello,"DAVID":clean_david,"FASTA Metadata":clean_fasta_metadata}

    # -----------------------------
    # Tool windows with corrected layout
    # -----------------------------
    def open_cleaner_window(tool_name):
        win = tk.Toplevel(root)
        win.title(f"{tool_name} Cleaner")
        win.geometry("500x400")

        tk.Label(win, text="How many files would you like to clean?").pack(pady=10)
        entry = tk.Entry(win); entry.pack(pady=5)

        selected_files, btns = [], []
        file_buttons_frame = tk.Frame(win)  # Created but not packed yet
        clean_btn = tk.Button(win, text="Clean", bg="lightblue",
                              command=lambda: tool_cleaners[tool_name](selected_files))

        def check_all_selected(n):
            if len(selected_files)==n and all(selected_files):
                clean_btn.pack(pady=20)
            else:
                clean_btn.forget()

        def generate_file_buttons():
            # Pack frame only after Confirm is clicked
            file_buttons_frame.pack(pady=10)
            for w in file_buttons_frame.winfo_children(): w.destroy()
            selected_files.clear(); btns.clear()
            try:
                n=int(entry.get()); 
                if n<=0: raise ValueError
            except ValueError:
                messagebox.showerror("Error","Enter a positive integer."); return
            for i in range(n):
                def pick_file(idx=i):
                    path=filedialog.askopenfilename(title=f"Select File {idx+1}")
                    if path:
                        if len(selected_files)<n: selected_files.append(path)
                        else: selected_files[idx]=path
                        btns[idx].config(text=f"File {idx+1}: {os.path.basename(path)}")
                        check_all_selected(n)
                btn=tk.Button(file_buttons_frame,text=f"Select File {i+1}",
                              command=lambda idx=i: pick_file(idx))
                btn.grid(row=i,column=0,sticky="w",pady=2)
                btns.append(btn)

        tk.Button(win,text="Confirm",command=generate_file_buttons).pack(pady=5)

    for tool in tool_cleaners:
        tk.Button(container,text=tool,width=20,height=2,
                  command=lambda t=tool: open_cleaner_window(t)).pack(pady=10)

    root.mainloop()

if __name__=="__main__":
    launch_gui()
