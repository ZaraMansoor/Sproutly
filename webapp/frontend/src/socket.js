/**
 * References:
 * https://websocket-client.readthedocs.io/en/latest/examples.html
 */
const socket = new WebSocket('ws://localhost:8000/ws/sproutly/');

socket.onopen = () => {
    console.log('WebSocket connection opened');
};

socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log("Received data from websocket:",data);
};

socket.onclose = () => {
    console.log('WebSocket connection closed');
}

export default socket;