import tkinter as tk
from tkinter import ttk, filedialog

# Function to read the links file and remove duplicates
def read_links(file_path):
    with open(file_path, 'r') as file:
        links_set = set(line.strip() for line in file)
    return sorted(links_set)

class LinkSearcherApp:
    def __init__(self, root):
        self.root = root
        self.links = []

        self.root.title("CloudHarvestDirect Link Searcher")

        # Set dark mode
        self.root.configure(bg='#2e2e2e')
        
        # File selection button
        self.file_button = tk.Button(root, text="Select Master Links File", command=self.load_file, bg='#4d4d4d', fg='white')
        self.file_button.pack(pady=10)

        # Input box for search
        self.search_label = tk.Label(root, text="Search:", fg="white", bg='#2e2e2e')
        self.search_label.pack(pady=5)
        
        self.search_entry = tk.Entry(root, width=80)
        self.search_entry.pack(pady=5)

        # Search button
        self.search_button = tk.Button(root, text="Search", command=self.search, bg='#4d4d4d', fg='white')
        self.search_button.pack(pady=5)

        # Save button
        self.save_button = tk.Button(root, text="Save Search Output", command=self.save_output, bg='#4d4d4d', fg='white')
        self.save_button.pack(pady=5)

        # Clear button
        self.clear_button = tk.Button(root, text="Clear Searches", command=self.clear_searches, bg='#4d4d4d', fg='white')
        self.clear_button.pack(pady=5)

        # Result display
        self.result_frame = tk.Frame(root, bg='#2e2e2e')
        self.result_frame.pack(pady=10)

        self.result_text = tk.Text(self.result_frame, width=100, height=20, bg='#1e1e1e', fg='white', selectbackground='#3e3e3e')
        self.result_text.pack(side="left", fill="y")

        self.scrollbar = tk.Scrollbar(self.result_frame, orient="vertical", command=self.result_text.yview)
        self.scrollbar.pack(side="right", fill="y")

        self.result_text.config(yscrollcommand=self.scrollbar.set)

        # Logbox for messages
        self.logbox = tk.Text(root, height=4, bg='#1e1e1e', fg='white', state=tk.DISABLED)
        self.logbox.pack(fill="x", pady=5)

        # Initial warning message
        self.log_message("PROGRAM MAY SAY NOT RESPONDING WHILE LOADING A LARGE MASTER LINKS FILE JUST WAIT 30 SECONDS - WDU", "red")

    def load_file(self):
        file_path = filedialog.askopenfilename(
            title="Select the Master Link File",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if file_path:
            self.links = read_links(file_path)
            self.log_message("Master File Loaded Successfully", "green")

    def search(self):
        query = self.search_entry.get().lower()
        self.result_text.delete(1.0, tk.END)
        results = [link for link in self.links if query in link.lower()]
        
        for result in results:
            self.result_text.insert(tk.END, result + "\n")

    def clear_searches(self):
        self.search_entry.delete(0, tk.END)
        self.result_text.delete(1.0, tk.END)

    def save_output(self):
        output_file = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if output_file:
            with open(output_file, 'w') as file:
                file.write(self.result_text.get(1.0, tk.END))
            self.log_message(f"Search output saved as {output_file}", "green")

    def log_message(self, message, color="white"):
        self.logbox.config(state=tk.NORMAL)
        self.logbox.insert(tk.END, message + "\n", "color")
        self.logbox.tag_configure("color", foreground=color)
        self.logbox.config(state=tk.DISABLED)
        self.logbox.see(tk.END)

# Initialize the GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = LinkSearcherApp(root)
    root.mainloop()
