import json

from channels.generic.websocket import AsyncWebsocketConsumer


class SensorConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("WebSocket attempted!")
        await self.accept()
        print("WebSocket connected!")


    async def disconnect(self, close_code):
        pass
        print(f"WebSocket disconnected! {close_code}")

    async def receive(self, text_data):
        data_json = json.loads(text_data)
        print("Received data:", data_json)

        message = data_json['message']

        await self.send(text_data=json.dumps({
            'message': message,
            'temperature': data_json['temperature'],
            'humidity': data_json['humidity'], # fix later
        }))