import json

from channels.generic.websocket import AsyncWebsocketConsumer


class SensorConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("WebSocket attempted!")
        await self.channel_layer.group_add("sproutly_sensor_data", self.channel_name)
        await self.channel_layer.group_add("sproutly_health_status", self.channel_name)
        await self.accept()
        print("WebSocket connected!")


    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("sproutly_sensor_data", self.channel_name)
        await self.channel_layer.group_discard("sproutly_health_status", self.channel_name)
        print(f"WebSocket disconnected! {close_code}")

    # received message from websocket. send to frontend
    async def sensorDataUpdate(self, event):
        try:
            print("Sending sensor data:", event["data"])
            await self.send(text_data=json.dumps(event["data"]))
        except Exception as e:
            print("Error sending sensor data:", e)

    async def healthUpdate(self, event):
        try:
            print("Sending health status:", event["data"])
            await self.send(text_data=json.dumps(event["data"]))
        except Exception as e:
            print("Error sending health status:", e)