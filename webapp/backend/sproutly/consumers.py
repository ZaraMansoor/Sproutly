'''
References for Channels: https://channels.readthedocs.io/en/stable/topics/consumers.html
'''

import json

from channels.generic.websocket import AsyncWebsocketConsumer


class SensorConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("WebSocket attempted!")
        await self.channel_layer.group_add("sproutly_sensor_data", self.channel_name)
        await self.channel_layer.group_add("sproutly_health_status", self.channel_name)
        await self.channel_layer.group_add("sproutly_plant_detection", self.channel_name)
        await self.accept()
        print("WebSocket connected!")


    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("sproutly_sensor_data", self.channel_name)
        await self.channel_layer.group_discard("sproutly_health_status", self.channel_name)
        await self.channel_layer.group_discard("sproutly_plant_detection", self.channel_name)
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

    async def plantDetectionUpdate(self, event):
        try:
            print("Sending plant detection:", event["data"])
            await self.send(text_data=json.dumps(event["data"]))
        except Exception as e:
            print("Error sending plant detection:", e)


class ActuatorConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("WebSocket attempted!")
        await self.channel_layer.group_add("sproutly_actuator_status", self.channel_name)
        await self.accept()
        print("WebSocket connected!")


    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("sproutly_actuator_status", self.channel_name)
        print(f"WebSocket disconnected! {close_code}")

    async def actuatorStatusUpdate(self, event):
        try:
            print("Sending actuator status:", event["data"])
            await self.send(text_data=json.dumps(event["data"]))
        except Exception as e:
            print("Error sending actuator status:", e)
