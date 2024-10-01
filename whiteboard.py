import tkinter as tk
from tkinter import colorchooser

class Whiteboard:
    def __init__(self, master):
        self.master = master
        self.master.title("Interactive Whiteboard")
        
        self.canvas = tk.Canvas(self.master, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.setup_tools()
        
        self.canvas.bind("<B1-Motion>", self.paint)
        self.canvas.bind("<ButtonRelease-1>", self.reset)
        
        self.old_x = None
        self.old_y = None
        self.color = "black"
        self.line_width = 2

    def setup_tools(self):
        tools = tk.Frame(self.master)
        tools.pack(side=tk.TOP, fill=tk.X)
        
        tk.Button(tools, text="Color", command=self.choose_color).pack(side=tk.LEFT)
        tk.Scale(tools, from_=1, to=10, orient=tk.HORIZONTAL, label="Line Width",
                 command=self.set_line_width).pack(side=tk.LEFT)
        tk.Button(tools, text="Clear", command=self.clear_canvas).pack(side=tk.LEFT)

    def paint(self, event):
        if self.old_x and self.old_y:
            self.canvas.create_line(self.old_x, self.old_y, event.x, event.y,
                                    width=self.line_width, fill=self.color,
                                    capstyle=tk.ROUND, smooth=tk.TRUE)
        self.old_x = event.x
        self.old_y = event.y

    def reset(self, event):
        self.old_x = None
        self.old_y = None

    def choose_color(self):
        color = colorchooser.askcolor(color=self.color)[1]
        if color:
            self.color = color

    def set_line_width(self, value):
        self.line_width = int(value)

    def clear_canvas(self):
        self.canvas.delete("all")

if __name__ == "__main__":
    root = tk.Tk()
    whiteboard = Whiteboard(root)
    root.geometry("800x600")
    root.mainloop()
