import tkinter as tk
from tkinter import filedialog
import os

def parse_file(file_path):
    cog_dict = {}
    with open(file_path, 'r') as f:
        lines = f.read().splitlines()

    current_code = None
    current_title = None

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
        all_protein_sets = []
        for i in present_files:
            cog_info = file_data_list[i].get(code, {})
            title = cog_info.get("title", title)
            proteins = set(cog_info.get("proteins", []))
            all_protein_sets.append(proteins)

        results.append(f"{code}: {title}")

        for i, proteins in enumerate(all_protein_sets):
            others = set().union(*(s for j, s in enumerate(all_protein_sets) if j != i))
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

def launch_gui():
    root = tk.Tk()
    root.title("Multi-File COG Comparator")
    root.geometry("600x650")

    file_labels = []

    # Center frame to hold everything
    container = tk.Frame(root)
    container.pack(expand=True)

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
            label = tk.Label(frame, text="", wraplength=500, justify='center')
            label.pack()
            tk.Button(frame, text="Browse", command=lambda lbl=label: browse_file(lbl)).pack(pady=2)

            file_labels.append(label)

    def browse_file(label):
        path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if path:
            label.config(text=path)

    def process():
        file_paths = [lbl.cget("text") for lbl in file_labels]
        if not all(file_paths):
            messagebox.showerror("Error", "Please select all files.")
            return

        output_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if not output_path:
            return

        try:
            process_files(file_paths, output_path)
            messagebox.showinfo("Done", f"File saved to: {output_path}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred:\n{e}")

    # Entry for number of files
    tk.Label(container, text="How many files do you want to compare? (≥ 2)", justify="center").pack(pady=10)
    file_count_entry = tk.Entry(container, justify='center')
    file_count_entry.pack()
    tk.Button(container, text="Confirm", command=get_file_count).pack(pady=5)

    # Frame to hold file selection inputs
    file_input_frame = tk.Frame(container)
    file_input_frame.pack(pady=10)

    # Compare button
    tk.Button(container, text="Compare Files", command=process, bg='green', fg='white').pack(pady=20)

    root.mainloop()

# Run GUI
if __name__ == "__main__":
    launch_gui()
