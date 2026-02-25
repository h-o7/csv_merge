# merge_two_csvs_gui_case_insensitive.py
"""
GUI tool to merge two CSV files based on columns A and B (case-insensitive + trimmed),
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
        self.root.title("Merge Two CSVs - A + B → C (case-insensitive)")
        self.root.geometry("620x400")
        self.root.resizable(False, False)

        self.file1_path = None
        self.file2_path = None

        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.root, text="Merge two CSV files", font=("Segoe UI", 14, "bold")).pack(pady=(15, 5))

        tk.Label(self.root,
                 text="Match on columns 'A' and 'B' (case-insensitive + trimmed whitespace)\n"
                      "New column 'C' gets value from File 2\n\n"
                      "Original casing & values are preserved in output",
                 font=("Segoe UI", 10), justify="left").pack(pady=(0, 15))

        # File 1
        frame1 = tk.Frame(self.root)
        frame1.pack(fill="x", padx=20, pady=5)

        tk.Label(frame1, text="File 1 (base):", width=14, anchor="w").pack(side="left")
        self.label_file1 = tk.Label(frame1, text="not selected", fg="grey", anchor="w")
        self.label_file1.pack(side="left", fill="x", expand=True, padx=(10, 0))

        tk.Button(frame1, text="Browse...", command=self.select_file1, width=10).pack(side="right")

        # File 2
        frame2 = tk.Frame(self.root)
        frame2.pack(fill="x", padx=20, pady=8)

        tk.Label(frame2, text="File 2 (values):", width=14, anchor="w").pack(side="left")
        self.label_file2 = tk.Label(frame2, text="not selected", fg="grey", anchor="w")
        self.label_file2.pack(side="left", fill="x", expand=True, padx=(10, 0))

        tk.Button(frame2, text="Browse...", command=self.select_file2, width=10).pack(side="right")

        tk.Label(self.root, text="Output: merged_result.csv (or merged_result_2.csv etc.)",
                 fg="#555", font=("Segoe UI", 9)).pack(pady=(10, 5))

        tk.Button(self.root, text="MERGE FILES", font=("Segoe UI", 12, "bold"),
                  bg="#4CAF50", fg="white", padx=30, pady=12,
                  command=self.merge_files).pack(pady=25)

        self.status = tk.Label(self.root, text="", fg="#444", wraplength=580)
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
            df1 = pd.read_csv(self.file1_path)
            df2 = pd.read_csv(self.file2_path)

            # Check required columns
            for df, name in [(df1, "File 1"), (df2, "File 2")]:
                if 'A' not in df.columns or 'B' not in df.columns:
                    raise ValueError(f"Column 'A' or 'B' missing in {name}")

            # Prepare normalized keys for matching (case-insensitive + trimmed)
            df1 = df1.copy()
            df2 = df2.copy()

            df1['__A_norm'] = df1['A'].astype(str).str.lower().str.strip()
            df1['__B_norm'] = df1['B'].astype(str).str.lower().str.strip()

            df2['__A_norm'] = df2['A'].astype(str).str.lower().str.strip()
            df2['__B_norm'] = df2['B'].astype(str).str.lower().str.strip()

            # Find the value column from file 2 (first column that's not A or B)
            value_cols = [col for col in df2.columns if col not in ['A', 'B', '__A_norm', '__B_norm']]
            if not value_cols:
                raise ValueError("No data column found in File 2 (only A and B present?)")

            value_col = value_cols[0]
            print(f"Using column '{value_col}' from File 2 → new column 'C'")

            # Create lookup: normalized (A,B) → original value
            lookup = df2.set_index(['__A_norm', '__B_norm'])[value_col].to_dict()

            # Add C to df1 using normalized keys
            df1['C'] = df1.apply(
                lambda row: lookup.get((row['__A_norm'], row['__B_norm']), pd.NA),
                axis=1
            )

            # Clean up temporary columns
            df1 = df1.drop(columns=['__A_norm', '__B_norm'])

            # Save result
            output_path = "merged_result.csv"
            i = 1
            while os.path.exists(output_path):
                output_path = f"merged_result_{i}.csv"
                i += 1

            df1.to_csv(output_path, index=False)

            msg = f"Success!\n\nSaved to:\n{output_path}\n\nRows: {len(df1)}"
            messagebox.showinfo("Merge Complete", msg)
            self.status.config(text=f"Saved → {output_path}", fg="darkgreen")

        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.status.config(text="Failed – check error message", fg="red")


if __name__ == "__main__":
    root = tk.Tk()
    app = CSV Merger App(root)
    root.mainloop()