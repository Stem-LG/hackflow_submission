const WebSocket = require("ws");
const wss = new WebSocket.Server({ port: 8080 });

// Handle connections
wss.on("connection", (ws) => {
    console.log("Client connected");

    // Handle incoming messages
    ws.on("message", (message) => {
        console.log(`Received message => ${message}`);

        // Echo back the received message
        ws.send(`Server Response: ${message}`);

        // Broadcast to all clients
        wss.clients.forEach((client) => {
            if (client.readyState === WebSocket.OPEN) {
                client.send(`${message}`);
            }
        });
    });

    // Handle errors
    ws.on("error", (error) => {
        console.error("Error occurred");
        console.log(error);
    });

    // Handle connection close
    ws.on("close", () => {
        console.log("Client disconnected");
    });
});

console.log("WebSocket Server listening on port 8080");
