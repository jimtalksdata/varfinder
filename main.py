import tkinter as tk
from tkinter import filedialog, ttk
from tkcalendar import DateEntry
import pandas as pd
import datetime
import yaml


class FileLoader:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("VarFinder")
        self.columns_to_show = ["chr", "pos", "ref",
                                "alt", "classification", "curation", "enterDate"]
        self.window_width = 1400
        self.max_results_to_show = 10

        self.file_path = tk.StringVar()
        self.dataframe = None

        self.load_prefs()
        self.create_widgets()
        # bind enter to filter button
        self.window.bind('<Return>', lambda event=None: self.filter_button.invoke())
        # self.window.bind('<Control-c>', self.copy_to_clipboard)

    def load_prefs(self):
        try:
            with open('prefs.yaml', 'r') as f:
                prefs = yaml.safe_load(f)
                if 'file_path' in prefs:
                    self.file_path.set(prefs['file_path'])
        except FileNotFoundError:
            pass  # It's okay if the file doesn't exist

    def save_prefs(self):
        prefs = {'file_path': self.file_path.get()}
        with open('prefs.yaml', 'w') as f:
            yaml.safe_dump(prefs, f)

    def create_widgets(self):
        tk.Label(self.window, text='File path:').grid(
            row=0, column=0, padx=10, pady=10)

        self.file_entry = tk.Entry(
            self.window, textvariable=self.file_path, width=50)
        self.file_entry.grid(row=0, column=1, padx=10)

        self.browse_button = tk.Button(
            self.window, text='Browse...', command=self.browse_files)
        self.browse_button.grid(row=0, column=2, padx=10)

        self.load_button = tk.Button(
            self.window, text='Reload CSV', command=self.load_file)
        self.load_button.grid(row=0, column=3, padx=10)

        self.filter_button = tk.Button(
            self.window, text='Filter (Enter)', command=self.filter_data)
        self.filter_button.grid(row=0, column=4, padx=10)

        self.create_filter_widgets()
        self.create_table()
        self.create_textbox()
        self.create_status_bar()

    def create_status_bar(self):
        self.status_var = tk.StringVar()
        self.status_bar = tk.Label(
            self.window, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor='w')
        self.status_bar.grid(row=5, column=0, columnspan=12, sticky='we')

    def refresh_record_count(self):
        num_rows = len(self.dataframe)
        self.update_status(f'{num_rows} rows loaded')

    def refresh_filter_results(self, df):
        num_rows = len(df)
        self.update_status(
            f'{num_rows} rows filtered, showing most recent {self.max_results_to_show}')

    def update_status(self, message):
        self.status_var.set(message)

    def copy_to_clipboard(self, event):
        selected_item = self.table.selection()[0]  # get selected item
        curation_value = self.table.set(selected_item, 'curation')
        self.window.clipboard_clear()  # clear clipboard contents
        # append new value to clipboard
        self.window.clipboard_append(curation_value)

    def create_filter_widgets(self):
        tk.Label(self.window, text='chr:').grid(row=1, column=0, padx=10)
        self.chr_entry = tk.Entry(self.window)
        self.chr_entry.grid(row=1, column=1)

        tk.Label(self.window, text='pos:').grid(row=1, column=2, padx=10)
        self.pos_entry = tk.Entry(self.window)
        self.pos_entry.grid(row=1, column=3)

        tk.Label(self.window, text='ref:').grid(row=1, column=4, padx=10)
        self.ref_entry = tk.Entry(self.window)
        self.ref_entry.grid(row=1, column=5)

        tk.Label(self.window, text='alt:').grid(row=1, column=6, padx=10)
        self.alt_entry = tk.Entry(self.window)
        self.alt_entry.grid(row=1, column=7)

        tk.Label(self.window, text='classification:').grid(
            row=1, column=8, padx=10)
        self.classification_combobox = ttk.Combobox(
            self.window, values=["Not set", "Pathogenic", "Likely Pathogenic"])
        self.classification_combobox.grid(row=1, column=9)

        tk.Label(self.window, text='somatic:').grid(row=1, column=10, padx=10)
        self.somatic_combobox = ttk.Combobox(self.window, values=[
                                             "Not set", "Somatic", "Not Confirmed Somatic", "Germline", "Artifact"])
        self.somatic_combobox.grid(row=1, column=11)

        tk.Label(self.window, text='curation:').grid(row=2, column=0, padx=10)
        self.curation_entry = tk.Entry(self.window)
        self.curation_entry.grid(row=2, column=1)

        tk.Label(self.window, text='From date:').grid(row=2, column=2, padx=10)
        self.from_date = DateEntry(self.window)
        self.from_date.grid(row=2, column=3)

        # default from date to 1 year ago
        self.from_date.set_date(
            datetime.date.today() - datetime.timedelta(days=365))

        tk.Label(self.window, text='To date:').grid(row=2, column=4, padx=10)
        self.to_date = DateEntry(self.window)
        self.to_date.grid(row=2, column=5)

    def create_table(self):
        self.table = ttk.Treeview(self.window)
        self.table["columns"] = self.columns_to_show
        self.table['show'] = 'headings'
        total_width = self.window_width
        curation_width = int(total_width * 2/3)
        other_width = int((total_width - curation_width) /
                          (len(self.columns_to_show) - 1))

        for column in self.table["columns"]:
            if column == 'curation':
                self.table.column(column, width=curation_width)
            else:
                self.table.column(column, width=other_width)
            self.table.heading(column, text=column)

        self.table.grid(row=3, column=0, columnspan=12, padx=10, pady=10)
        self.table.bind('<<TreeviewSelect>>', self.update_textbox)

    def create_textbox(self):
        self.textbox = tk.Text(self.window, height=10)
        self.textbox.grid(row=4, column=0, columnspan=12,
                          padx=20, pady=10, sticky='WE')
        self.textbox.config(state='disabled')  # make the textbox read-only

    def update_textbox(self, event):
        self.textbox.config(state='normal')  # make the textbox writable
        self.textbox.delete('1.0', 'end')  # clear the textbox

        selected_item = self.table.selection()[0]  # get selected item
        curation_value = self.table.set(selected_item, 'curation')
        self.textbox.insert('end', curation_value)  # insert the new value

        self.window.clipboard_clear()  # clear clipboard contents
        # append new value to clipboard
        self.window.clipboard_append(curation_value)

        # make the textbox read-only again
        self.textbox.config(state='disabled')

    def update_table(self, df):
        for i in self.table.get_children():
            self.table.delete(i)
        df = df[self.columns_to_show].head(self.max_results_to_show)
        for index, row in df.iterrows():
            self.table.insert('', 'end', values=tuple(row))

    def browse_files(self):
        file_name = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv")])
        self.file_path.set(file_name)
        self.load_file()

    def load_file(self):
        if self.file_path.get():
            self.dataframe = pd.read_csv(self.file_path.get(), sep=',')
            self.dataframe = self.dataframe.fillna("")
            self.refresh_record_count()
            print("File loaded successfully into DataFrame.")
        else:
            print("No file selected.")

    def filter_data(self):
        if self.dataframe is None and self.file_path.get() is not None:
            self.load_file()
        if self.dataframe is not None:
            df_filtered = self.dataframe

            chr_filter = self.chr_entry.get()
            pos_filter = self.pos_entry.get()
            ref_filter = self.ref_entry.get()
            alt_filter = self.alt_entry.get()
            classification_filter = self.classification_combobox.get()
            somatic_filter = self.somatic_combobox.get()
            from_date_filter = self.from_date.get_date()
            to_date_filter = self.to_date.get_date()
            curation_filter = self.curation_entry.get().lower()

            # split curation filter into a list and search each term separately, delimited by space
            curation_filter_list = curation_filter.split()

            # change from date to datetime64
            from_date_filter = datetime.datetime.combine(
                from_date_filter, datetime.datetime.min.time())
            to_date_filter = datetime.datetime.combine(
                to_date_filter, datetime.datetime.min.time())

            if chr_filter:
                df_filtered = df_filtered[df_filtered['chr'] == chr_filter]
            if pos_filter:
                df_filtered = df_filtered[df_filtered['pos'] == int(
                    pos_filter)]
            if ref_filter:
                df_filtered = df_filtered[df_filtered['ref'] == ref_filter]
            if alt_filter:
                df_filtered = df_filtered[df_filtered['alt'] == alt_filter]
            if classification_filter:
                df_filtered = df_filtered[df_filtered['classification']
                                          == classification_filter]
            if somatic_filter:
                df_filtered = df_filtered[df_filtered['somatic']
                                          == somatic_filter]
            if curation_filter:
                for term in curation_filter_list:
                    df_filtered = df_filtered[df_filtered['curation'].str.lower(
                    ).str.contains(term)]

            df_filtered = df_filtered[(pd.to_datetime(df_filtered['enterDate']) >= from_date_filter) &
                                      (pd.to_datetime(df_filtered['enterDate']) <= to_date_filter)]

            # sort by enterDate descending
            df_filtered = df_filtered.sort_values(
                by=['enterDate'], ascending=False)

            self.refresh_filter_results(df_filtered)
            self.update_table(df_filtered)

    def run(self):
        self.window.mainloop()
        self.save_prefs()


if __name__ == "__main__":
    app = FileLoader()
    app.run()
