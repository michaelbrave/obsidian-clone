import os
import re
import tkinter as tk
from tkinter import filedialog, scrolledtext
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
        # File list
        self.file_listbox = tk.Listbox(self.master, width=30)
        self.file_listbox.pack(side=tk.LEFT, fill=tk.Y)
        self.file_listbox.bind('<<ListboxSelect>>', self.open_selected_file)

        # Text editor
        self.text_editor = scrolledtext.ScrolledText(self.master, wrap=tk.WORD)
        self.text_editor.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        # Buttons
        button_frame = tk.Frame(self.master)
        button_frame.pack(side=tk.TOP, fill=tk.X)

        tk.Button(button_frame, text="New File", command=self.new_file).pack(side=tk.LEFT)
        tk.Button(button_frame, text="Open File", command=self.open_file).pack(side=tk.LEFT)
        tk.Button(button_frame, text="Save", command=self.save_file).pack(side=tk.LEFT)
        tk.Button(button_frame, text="Show Graph", command=self.show_graph).pack(side=tk.LEFT)

    def new_file(self):
        filename = filedialog.asksaveasfilename(defaultextension=".md")
        if filename:
            self.current_file = filename
            self.text_editor.delete(1.0, tk.END)
            self.update_file_list()

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
        self.update_file_list()
        self.update_graph()

    def open_selected_file(self, event):
        selection = self.file_listbox.curselection()
        if selection:
            filename = self.file_listbox.get(selection[0])
            self.load_file(filename)

    def save_file(self):
        if self.current_file:
            content = self.text_editor.get(1.0, tk.END)
            with open(self.current_file, 'w') as file:
                file.write(content)
            self.update_graph()

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
                if link in self.files:
                    self.graph.add_edge(filename, link)

    def show_graph(self):
        plt.clf()
        pos = nx.spring_layout(self.graph)
        nx.draw(self.graph, pos, with_labels=True, node_color='lightblue', node_size=500, font_size=8)
        
        graph_window = tk.Toplevel(self.master)
        graph_window.title("File Connections Graph")
        
        canvas = FigureCanvasTkAgg(plt.gcf(), master=graph_window)
        canvas.draw()
        canvas.get_tk_widget().pack()

    def run(self):
        self.master.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = ObsidianLikeApp(root)
    app.run()
