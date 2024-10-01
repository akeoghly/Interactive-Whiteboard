document.addEventListener('DOMContentLoaded', () => {
    const socket = io();
    const canvas = document.getElementById('whiteboard');
    const ctx = canvas.getContext('2d');
    const brushSize = document.getElementById('brushSize');
    const clearBtn = document.getElementById('clearBtn');
    const qrcodeElement = document.getElementById('qrcode');

    let isDrawing = false;
    let clientColor = '#000000';

    // Generate QR code
    const protocol = window.location.protocol;
    const hostname = window.location.hostname;
    const port = window.location.port;
    const url = `${protocol}//${hostname}${port ? ':' + port : ''}`;
    new QRCode(qrcodeElement, {
        text: url,
        width: 128,
        height: 128
    });

    // Request a color from the server
    socket.emit('requestColor');

    // Set canvas size
    function resizeCanvas() {
        canvas.width = window.innerWidth * 0.8;
        canvas.height = window.innerHeight * 0.8;
    }
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);


    socket.on('setColor', (color) => {
        clientColor = color;
        console.log('Assigned color:', clientColor);
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
        let x, y;

        if (e.type === 'mousemove') {
            x = e.clientX - rect.left;
            y = e.clientY - rect.top;
        } else if (e.type === 'touchmove') {
            x = e.touches[0].clientX - rect.left;
            y = e.touches[0].clientY - rect.top;
        }

        ctx.lineWidth = brushSize.value;
        ctx.lineCap = 'round';
        ctx.strokeStyle = clientColor;

        ctx.lineTo(x, y);
        ctx.stroke();
        ctx.beginPath();
        ctx.moveTo(x, y);

        socket.emit('draw', { x, y, brushSize: brushSize.value, color: clientColor });
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
    canvas.addEventListener('touchstart', startDrawing);
    canvas.addEventListener('touchmove', draw);
    canvas.addEventListener('touchend', stopDrawing);

    clearBtn.addEventListener('click', clearCanvas);
});
