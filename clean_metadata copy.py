import tkinter as tk
from tkinter import filedialog

def select_file():
    """Open a GUI file picker to select a UniProt text file."""
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Select UniProt downloaded text file",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )
    return file_path

def extract_fasta(input_file, output_file):
    """Parse the UniProt text file and extract clean FASTA records."""
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        entry_id = None
        sequence = []
        in_sequence = False

        for line in infile:
            line = line.strip()

            # Start of a new record (e.g. "ID   Q73NZ6_TREDE")
            if line.startswith("ID"):
                if entry_id and sequence:
                    outfile.write(f">{entry_id}\n")
                    outfile.write("".join(sequence) + "\n")
                entry_id = line.split()[1].split("_")[0]  # Extract "Q73NZ6" from "Q73NZ6_TREDE"
                sequence = []
                in_sequence = False

            elif line.startswith("SQ"):
                in_sequence = True
                continue

            elif line.startswith("//"):
                # End of record — write final sequence
                if entry_id and sequence:
                    outfile.write(f">{entry_id}\n")
                    outfile.write("".join(sequence) + "\n")
                entry_id = None
                sequence = []
                in_sequence = False

            elif in_sequence:
                # Accumulate sequence lines
                sequence.append("".join(filter(str.isalpha, line)))  # Remove spaces & numbers

def main():
    input_path = select_file()
    if not input_path:
        print("❌ No file selected. Exiting.")
        return

    output_path = input_path.rsplit(".", 1)[0] + "_cleaned.txt"
    try:
        extract_fasta(input_path, output_path)
        print(f"✅ Cleaned FASTA records saved to: {output_path}")
    except Exception as e:
        print(f"❌ Error during processing: {e}")

if __name__ == "__main__":
    main()
