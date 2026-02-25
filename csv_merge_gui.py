# merge_two_csvs_gui.py
"""
Simple GUI tool to merge two CSV files based on columns A and B,
placing the value from the second file into a new column C.

Requirements:
    pip install pandas
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import os


class CSV Merger App:
    def __init__(self, root):
        self.root = root
        self.root.title("Merge Two CSVs - A + B → C")
        self.root.geometry("580x380")
        self.root.resizable(False, False)

        self.file1_path = None
        self.file2_path = None

        self.create_widgets()

    def create_widgets(self):
        # ── Title ───────────────────────────────────────────────
        tk.Label(self.root, text="Merge two CSV files", font=("Segoe UI", 14, "bold")).pack(pady=(15, 5))

        tk.Label(self.root, text="Match on columns 'A' and 'B'\nPut second file's value into new column 'C'",
                 font=("Segoe UI", 10), justify="left").pack(pady=(0, 15))

        # ── File 1 (left / base) ───────────────────────────────
        frame1 = tk.Frame(self.root)
        frame1.pack(fill="x", padx=20, pady=5)

        tk.Label(frame1, text="File 1 (base):", width=14, anchor="w").pack(side="left")
        self.label_file1 = tk.Label(frame1, text="not selected", fg="grey", anchor="w")
        self.label_file1.pack(side="left", fill="x", expand=True, padx=(10, 0))

        tk.Button(frame1, text="Browse...", command=self.select_file1, width=10).pack(side="right")

        # ── File 2 (right / values to add) ─────────────────────
        frame2 = tk.Frame(self.root)
        frame2.pack(fill="x", padx=20, pady=8)

        tk.Label(frame2, text="File 2 (values):", width=14, anchor="w").pack(side="left")
        self.label_file2 = tk.Label(frame2, text="not selected", fg="grey", anchor="w")
        self.label_file2.pack(side="left", fill="x", expand=True, padx=(10, 0))

        tk.Button(frame2, text="Browse...", command=self.select_file2, width=10).pack(side="right")

        # ── Output filename hint ───────────────────────────────
        tk.Label(self.root, text="Output will be saved as:  merged_result.csv", fg="#555",
                 font=("Segoe UI", 9)).pack(pady=(10, 5))

        # ── Merge button ───────────────────────────────────────
        tk.Button(self.root, text="MERGE FILES", font=("Segoe UI", 12, "bold"),
                  bg="#4CAF50", fg="white", padx=20, pady=10,
                  command=self.merge_files).pack(pady=25)

        # Status label
        self.status = tk.Label(self.root, text="", fg="#444", wraplength=540)
        self.status.pack(pady=5)

    def select_file1(self):
        path = filedialog.askopenfilename(
            title="Select first CSV (base file)",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if path:
            self.file1_path = path
            self.label_file1.config(text=os.path.basename(path), fg="black")
            self.status.config(text="")

    def select_file2(self):
        path = filedialog.askopenfilename(
            title="Select second CSV (values to add)",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if path:
            self.file2_path = path
            self.label_file2.config(text=os.path.basename(path), fg="black")
            self.status.config(text="")

    def merge_files(self):
        if not self.file1_path or not self.file2_path:
            messagebox.showwarning("Missing files", "Please select both CSV files first.")
            return

        self.status.config(text="Processing...", fg="blue")
        self.root.update()

        try:
            # Read both files
            df1 = pd.read_csv(self.file1_path)
            df2 = pd.read_csv(self.file2_path)

            # Make sure required columns exist
            for df, name in [(df1, "File 1"), (df2, "File 2")]:
                if 'A' not in df.columns or 'B' not in df.columns:
                    raise ValueError(f"Column 'A' or 'B' not found in {name}")

            # We'll assume the value we want to bring over is the first column that is neither A nor B
            value_cols = [col for col in df2.columns if col not in ['A', 'B']]
            if not value_cols:
                raise ValueError("No data columns found in File 2 (only A and B?)")

            # For simplicity we take the first remaining column as the value to move
            value_col = value_cols[0]
            print(f"Using column '{value_col}' from File 2 as source for column C")

            # Create lookup dictionary:  (A,B) → value
            lookup = df2.set_index(['A', 'B'])[value_col].to_dict()

            # Add column C to df1
            df1['C'] = df1.apply(
                lambda row: lookup.get((row['A'], row['B']), pd.NA),
                axis=1
            )

            # Save result
            output_path = "merged_result.csv"
            i = 1
            while os.path.exists(output_path):
                output_path = f"merged_result_{i}.csv"
                i += 1

            df1.to_csv(output_path, index=False)

            msg = f"Success!\n\nSaved to:\n{output_path}\n\nRows in result: {len(df1)}"
            messagebox.showinfo("Merge Complete", msg)
            self.status.config(text=f"Saved → {output_path}", fg="darkgreen")

        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.status.config(text="Failed – see error message", fg="red")


if __name__ == "__main__":
    root = tk.Tk()
    app = CSV Merger App(root)
    root.mainloop()