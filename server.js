const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const path = require('path');

const app = express();
const server = http.createServer(app);
const io = socketIo(server);

app.use(express.static(path.join(__dirname, '.')));

const PORT = process.env.PORT || 3000;
const IP = '0.0.0.0';  // Listen on all network interfaces

let connectedClients = 0;
const colors = ['#FF0000', '#00FF00', '#0000FF', '#FFFF00', '#FF00FF', '#00FFFF'];

io.on('connection', (socket) => {
    const clientColor = colors[connectedClients % colors.length];
    connectedClients++;

    socket.emit('setColor', clientColor);

    socket.on('draw', (data) => {
        socket.broadcast.emit('draw', { ...data, color: clientColor });
    });

    socket.on('disconnect', () => {
        connectedClients--;
    });
});

server.listen(PORT, IP, () => {
    console.log(`Server running on http://${IP}:${PORT}`);
});
