import tkinter as tk
from tkinter import simpledialog, messagebox




class JobSearchUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Job Search Control Panel")
        self.keywords = tk.StringVar()
        self.location = tk.StringVar()
        self.filters = tk.StringVar()
        self.company_vars = {}
        self.company_list = ["Adzuna", "SerpApi", "Indeed", "ZipRecruiter", "Monster", "Built In", "JPMorgan"]
        self.result = None
        self._build_ui()

    def _build_ui(self):
        tk.Label(self.root, text="Keywords:").grid(row=0, column=0, sticky="e")
        tk.Entry(self.root, textvariable=self.keywords).grid(row=0, column=1)
        tk.Label(self.root, text="Location:").grid(row=1, column=0, sticky="e")
        tk.Entry(self.root, textvariable=self.location).grid(row=1, column=1)
        tk.Label(self.root, text="Filters (JSON):").grid(row=2, column=0, sticky="e")
        tk.Entry(self.root, textvariable=self.filters).grid(row=2, column=1)
        tk.Label(self.root, text="Companies/Boards to Scrape:").grid(row=3, column=0, sticky="ne")
        self.company_frame = tk.Frame(self.root)
        self.company_frame.grid(row=3, column=1, sticky="w")
        self._refresh_company_checkboxes()
        tk.Button(self.root, text="Add Board", command=self._add_company_dialog).grid(row=4, column=1, sticky="w")
        tk.Button(self.root, text="Remove Selected", command=self._remove_selected_companies).grid(row=5, column=1, sticky="w")
        tk.Button(self.root, text="Search", command=self._on_search).grid(row=6, column=0, columnspan=2)

    def _refresh_company_checkboxes(self):
        for widget in self.company_frame.winfo_children():
            widget.destroy()
        for i, company in enumerate(self.company_list):
            if company not in self.company_vars:
                self.company_vars[company] = tk.BooleanVar(value=True)
            cb = tk.Checkbutton(self.company_frame, text=company, variable=self.company_vars[company])
            cb.grid(row=i, column=0, sticky="w")

    def _add_company_dialog(self):
        new_company = simpledialog.askstring("Add Board", "Enter new company/board name:")
        if new_company and new_company not in self.company_list:
            self.company_list.append(new_company)
            self.company_vars[new_company] = tk.BooleanVar(value=True)
            self._refresh_company_checkboxes()

    def _remove_selected_companies(self):
        to_remove = [c for c in self.company_list if self.company_vars[c].get() is False]
        for c in to_remove:
            self.company_list.remove(c)
            del self.company_vars[c]
        self._refresh_company_checkboxes()

    def _on_search(self):
        try:
            filters = eval(self.filters.get()) if self.filters.get() else {}
        except Exception:
            messagebox.showerror("Error", "Filters must be valid JSON or Python dict.")
            return
        selected_companies = [c for c in self.company_list if self.company_vars[c].get()]
        self.result = {
            "keywords": self.keywords.get(),
            "location": self.location.get(),
            "filters": filters,
            "companies": selected_companies
        }
        self.root.quit()

    def get_search_params(self):
        self.root.mainloop()
        return self.result

if __name__ == "__main__":
    ui = JobSearchUI()
    params = ui.get_search_params()
    print(params)
