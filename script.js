document.addEventListener('DOMContentLoaded', () => {
    const socket = io();
    const canvas = document.getElementById('whiteboard');
    const ctx = canvas.getContext('2d');
    const brushSize = document.getElementById('brushSize');
    const clearBtn = document.getElementById('clearBtn');

    let isDrawing = false;
    let clientColor = '#000000';

    // Set canvas size
    canvas.width = 800;
    canvas.height = 600;

    // Generate QR Code
    const qrcode = new QRCode(document.getElementById("qrcode"), {
        text: window.location.href,
        width: 128,
        height: 128
    });

    socket.on('setColor', (color) => {
        clientColor = color;
    });

    function startDrawing(e) {
        isDrawing = true;
        draw(e);
    }

    function stopDrawing() {
        isDrawing = false;
        ctx.beginPath();
    }

    function draw(e) {
        if (!isDrawing) return;

        const rect = canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        ctx.lineWidth = brushSize.value;
        ctx.lineCap = 'round';
        ctx.strokeStyle = clientColor;

        ctx.lineTo(x, y);
        ctx.stroke();
        ctx.beginPath();
        ctx.moveTo(x, y);

        socket.emit('draw', { x, y, brushSize: brushSize.value });
    }

    function clearCanvas() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        socket.emit('clear');
    }

    socket.on('draw', (data) => {
        ctx.lineWidth = data.brushSize;
        ctx.lineCap = 'round';
        ctx.strokeStyle = data.color;

        ctx.lineTo(data.x, data.y);
        ctx.stroke();
        ctx.beginPath();
        ctx.moveTo(data.x, data.y);
    });

    socket.on('clear', clearCanvas);

    canvas.addEventListener('mousedown', startDrawing);
    canvas.addEventListener('mousemove', draw);
    canvas.addEventListener('mouseup', stopDrawing);
    canvas.addEventListener('mouseout', stopDrawing);

    clearBtn.addEventListener('click', clearCanvas);
});
