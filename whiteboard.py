import tkinter as tk
from tkinter import colorchooser
import threading
from flask import Flask, render_template_string
import socket

try:
    from flask_socketio import SocketIO
    SOCKETIO_AVAILABLE = True
except ImportError:
    SOCKETIO_AVAILABLE = False
    print("SocketIO functionality is not available. To enable it, please install the required package.")
    print("Run: pip install flask-socketio")

try:
    import qrcode
    from PIL import Image, ImageTk
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False
    print("QR code functionality is not available. To enable it, please install the required packages.")
    print("Run: pip install qrcode[pil] flask flask-socketio")

app = Flask(__name__)
socketio = SocketIO(app)

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

        self.setup_qr_code()

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

    def setup_qr_code(self):
        if QR_AVAILABLE:
            local_ip = socket.gethostbyname(socket.gethostname())
            url = f"http://{local_ip}:5000"
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(url)
            qr.make(fit=True)
            qr_image = qr.make_image(fill_color="black", back_color="white")
            qr_image = qr_image.resize((150, 150), Image.LANCZOS)
            self.qr_photo = ImageTk.PhotoImage(qr_image)
            
            qr_label = tk.Label(self.master, image=self.qr_photo)
            qr_label.pack(side=tk.BOTTOM)
        else:
            qr_label = tk.Label(self.master, text="QR Code not available\nInstall required packages to enable")
            qr_label.pack(side=tk.BOTTOM)

        threading.Thread(target=self.run_flask, daemon=True).start()

    def run_flask(self):
        if SOCKETIO_AVAILABLE:
            socketio.run(app, host='0.0.0.0', port=5000)
        else:
            print("SocketIO is not available. Running Flask without real-time functionality.")
            app.run(host='0.0.0.0', port=5000)

@app.route('/')
def index():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Whiteboard Controller</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    </head>
    <body>
        <div id="canvas" style="width: 100vw; height: 100vh; touch-action: none;"></div>
        <script>
            var socket = io();
            var canvas = document.getElementById('canvas');
            var drawing = false;

            function getRelativeCoordinates(event) {
                var rect = canvas.getBoundingClientRect();
                return {
                    x: (event.touches[0].clientX - rect.left) / rect.width,
                    y: (event.touches[0].clientY - rect.top) / rect.height
                };
            }

            canvas.addEventListener('touchstart', function(e) {
                e.preventDefault();
                drawing = true;
                var coords = getRelativeCoordinates(e);
                socket.emit('start_line', coords);
            });

            canvas.addEventListener('touchmove', function(e) {
                e.preventDefault();
                if (drawing) {
                    var coords = getRelativeCoordinates(e);
                    socket.emit('draw_line', coords);
                }
            });

            canvas.addEventListener('touchend', function(e) {
                e.preventDefault();
                drawing = false;
                socket.emit('end_line');
            });
        </script>
    </body>
    </html>
    ''')

if SOCKETIO_AVAILABLE:
    @socketio.on('start_line')
    def start_line(data):
        whiteboard.old_x = data['x'] * whiteboard.canvas.winfo_width()
        whiteboard.old_y = data['y'] * whiteboard.canvas.winfo_height()

    @socketio.on('draw_line')
    def draw_line(data):
        x = data['x'] * whiteboard.canvas.winfo_width()
        y = data['y'] * whiteboard.canvas.winfo_height()
        whiteboard.canvas.create_line(whiteboard.old_x, whiteboard.old_y, x, y,
                                      width=whiteboard.line_width, fill=whiteboard.color,
                                      capstyle=tk.ROUND, smooth=tk.TRUE)
        whiteboard.old_x = x
        whiteboard.old_y = y

    @socketio.on('end_line')
    def end_line():
        whiteboard.old_x = None
        whiteboard.old_y = None

if __name__ == "__main__":
    root = tk.Tk()
    whiteboard = Whiteboard(root)
    root.geometry("800x600")
    root.mainloop()
