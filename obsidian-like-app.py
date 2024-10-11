import os
import re
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class ObsidianLikeApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Obsidian-like App")
        self.master.geometry("800x600")

        self.current_file = None
        self.files = {}
        self.graph = nx.Graph()

        self.create_widgets()

    def create_widgets(self):
        # Main frame
        main_frame = tk.Frame(self.master)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Buttons frame
        button_frame = tk.Frame(main_frame)
        button_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        tk.Button(button_frame, text="New File", command=self.new_file).pack(side=tk.LEFT, padx=2)
        tk.Button(button_frame, text="Open File", command=self.open_file).pack(side=tk.LEFT, padx=2)
        tk.Button(button_frame, text="Save", command=self.save_file).pack(side=tk.LEFT, padx=2)
        tk.Button(button_frame, text="Show Graph", command=self.show_graph).pack(side=tk.LEFT, padx=2)

        # Content frame
        content_frame = tk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # File list
        file_frame = tk.Frame(content_frame, width=200)
        file_frame.pack(side=tk.LEFT, fill=tk.Y)
        file_frame.pack_propagate(False)

        self.file_listbox = tk.Listbox(file_frame)
        self.file_listbox.pack(fill=tk.BOTH, expand=True)
        self.file_listbox.bind('<<ListboxSelect>>', self.open_selected_file)

        # Text editor
        self.text_editor = scrolledtext.ScrolledText(content_frame, wrap=tk.WORD)
        self.text_editor.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        self.text_editor.bind("<Control-Button-1>", self.handle_link_click)

    def new_file(self):
        if self.current_file or self.text_editor.get(1.0, tk.END).strip():
            if not messagebox.askyesno("New File", "Do you want to create a new file? Any unsaved changes will be lost."):
                return

        self.text_editor.delete(1.0, tk.END)
        self.current_file = None
        messagebox.showinfo("New File", "New file created. Please type your content and save when ready.")

    def open_file(self):
        filename = filedialog.askopenfilename(filetypes=[("Markdown files", "*.md")])
        if filename:
            self.load_file(filename)

    def load_file(self, filename):
        self.current_file = filename
        with open(filename, 'r') as file:
            content = file.read()
        self.text_editor.delete(1.0, tk.END)
        self.text_editor.insert(tk.END, content)
        self.files[os.path.basename(filename)] = content
        self.update_file_list()
        self.update_graph()

    def open_selected_file(self, event):
        selection = self.file_listbox.curselection()
        if selection:
            filename = self.file_listbox.get(selection[0])
            full_path = os.path.join(os.path.dirname(self.current_file) if self.current_file else os.getcwd(), filename)
            self.load_file(full_path)

    def save_file(self):
        content = self.text_editor.get(1.0, tk.END).strip()
        if not content:
            messagebox.showwarning("Empty File", "Cannot save an empty file.")
            return

        if not self.current_file:
            filename = filedialog.asksaveasfilename(defaultextension=".md", filetypes=[("Markdown files", "*.md")])
            if not filename:
                return
            self.current_file = filename

        with open(self.current_file, 'w') as file:
            file.write(content)
        self.files[os.path.basename(self.current_file)] = content
        self.update_file_list()
        self.update_graph()
        messagebox.showinfo("File Saved", f"File saved successfully: {self.current_file}")

    def update_file_list(self):
        self.file_listbox.delete(0, tk.END)
        for filename in self.files.keys():
            self.file_listbox.insert(tk.END, filename)

    def update_graph(self):
        self.graph.clear()
        for filename, content in self.files.items():
            self.graph.add_node(filename)
            links = re.findall(r'\[\[(.*?)\]\]', content)
            for link in links:
                link_with_extension = f"{link}.md" if not link.endswith('.md') else link
                if link_with_extension in self.files:
                    self.graph.add_edge(filename, link_with_extension)

    def show_graph(self):
        if not self.files:
            messagebox.showinfo("No Files", "No files to display in the graph.")
            return

        plt.clf()
        pos = nx.spring_layout(self.graph)
        nx.draw(self.graph, pos, with_labels=True, node_color='lightblue', node_size=500, font_size=8)
        
        graph_window = tk.Toplevel(self.master)
        graph_window.title("File Connections Graph")
        
        canvas = FigureCanvasTkAgg(plt.gcf(), master=graph_window)
        canvas.draw()
        canvas.get_tk_widget().pack()

    def handle_link_click(self, event):
        index = self.text_editor.index(f"@{event.x},{event.y}")
        line, col = map(int, index.split('.'))
        
        line_content = self.text_editor.get(f"{line}.0", f"{line}.end")
        matches = list(re.finditer(r'\[\[(.*?)\]\]', line_content))
        
        for match in matches:
            start, end = match.span()
            if start <= col <= end:
                link_name = match.group(1)
                self.open_linked_file(link_name)
                break

    def open_linked_file(self, link_name):
        link_with_extension = f"{link_name}.md" if not link_name.endswith('.md') else link_name
        if link_with_extension in self.files:
            full_path = os.path.join(os.path.dirname(self.current_file) if self.current_file else os.getcwd(), link_with_extension)
            self.load_file(full_path)
        else:
            messagebox.showinfo("File Not Found", f"The file '{link_with_extension}' does not exist.")

    def run(self):
        self.master.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = ObsidianLikeApp(root)
    app.run()