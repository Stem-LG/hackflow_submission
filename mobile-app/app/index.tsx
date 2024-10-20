import { useEffect, useState } from "react";
import { Text, View } from "react-native";
import ArcReactorSvg from "./_components/arc-reactor";

export default function Home() {
    const [color, setColor] = useState("#09f");

    useEffect(() => {
        // WebSocket connection URL
        const webSocketURL = "ws://172.16.2.151:8080";

        // Create a new WebSocket instance
        let socket = new WebSocket(webSocketURL);

        // Event handler for when the WebSocket connection is established
        socket.onopen = () => {
            console.log("WebSocket connected.");
        };

        let timeoutId = null;

        // Event handler for when the WebSocket receives a message
        socket.onmessage = (event) => {
            // Parse the received message
            const data = event.data;

            const sentColor = data.slice(11);

            if (sentColor === "red") {
                // Immediately switch to red
                setColor("#f33");

                // If there is an existing timeout, clear it
                if (timeoutId!) {
                    clearTimeout(timeoutId);
                }

                // Set a new timeout to switch back to green after 2 seconds
                timeoutId = setTimeout(() => {
                    setColor("#09f");
                    timeoutId = null; // Reset the timeout ID
                }, 5000);
            }
        };

        // Event handler for WebSocket errors
        socket.onerror = (error) => {
            console.error("WebSocket error:", error);
        };

        // Clean up the WebSocket connection when the component is unmounted
        return () => {
            socket.close();
        };
    }, []); // Empty dependency

    return (
        <View
            className={`h-full w-full`}
            style={{
                backgroundColor: color,
            }}
        >
            <Text>{color}</Text>
            <ArcReactorSvg color={color} />
        </View>
    );
}
