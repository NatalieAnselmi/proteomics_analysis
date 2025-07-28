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

def compare_cogs(file1_data, file2_data, file1_title, file2_title):
    results = []
    all_codes = sorted(set(file1_data.keys()).union(file2_data.keys()))

    for code in all_codes:
        in_file1 = code in file1_data
        in_file2 = code in file2_data

        if in_file1 and in_file2:
            title = file1_data[code]["title"] if file1_data[code]["title"] else file2_data[code]["title"]
            proteins1 = set(file1_data[code]["proteins"])
            proteins2 = set(file2_data[code]["proteins"])

            diff1 = proteins1 - proteins2
            diff2 = proteins2 - proteins1

            if diff1 or diff2:
                results.append(f"{code}: {title}")
                results.append(f"Unique to {file1_title}:")
                results.append(', '.join(sorted(diff1)) if diff1 else "(none)")
                results.append(f"Unique to {file2_title}:")
                results.append(', '.join(sorted(diff2)) if diff2 else "(none)")
                results.append("")

        elif in_file1:
            title = file1_data[code]["title"]
            results.append(f"{code}: {title}")
            results.append(f"Unique to {file1_title}:")
            results.append(', '.join(sorted(file1_data[code]["proteins"])))
            results.append(f"Unique to {file2_title}:")
            results.append("(none)")
            results.append("")

        elif in_file2:
            title = file2_data[code]["title"]
            results.append(f"{code}: {title}")
            results.append(f"Unique to {file1_title}:")
            results.append("(none)")
            results.append(f"Unique to {file2_title}:")
            results.append(', '.join(sorted(file2_data[code]["proteins"])))
            results.append("")

    return results

def select_files():
    root = tk.Tk()
    root.withdraw()
    file1_path = filedialog.askopenfilename(title="Select File 1")
    file2_path = filedialog.askopenfilename(title="Select File 2")
    return file1_path, file2_path

def main():
    file1_path, file2_path = select_files()
    if not file1_path or not file2_path:
        print("File selection cancelled.")
        return

    file1_title = os.path.basename(file1_path)
    file2_title = os.path.basename(file2_path)

    file1_data = parse_file(file1_path)
    file2_data = parse_file(file2_path)

    results = compare_cogs(file1_data, file2_data, file1_title, file2_title)

    output_filename = "COG_comparison_results.txt"
    with open(output_filename, "w") as out_file:
        out_file.write("\n".join(results))

    print(f"Comparison complete. Output saved to {output_filename}")

if __name__ == "__main__":
    main()
