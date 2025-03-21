from django.shortcuts import render
import paho.mqtt.client as mqtt
import json
from django.http import JsonResponse

MQTT_SERVER = "broker.emqx.io"
CONTROL_TOPIC = "django/control"

def send_control_command(request):
    if request.method == "POST":
        data = json.loads(request.body)
        control_command = data.get("control_command")

        client = mqtt.Client()
        client.connect(MQTT_SERVER, 1883)
        client.publish(CONTROL_TOPIC, json.dumps(control_command))
        client.disconnect()

        return JsonResponse({"status": "Command Sent", "command": control_command})

    return JsonResponse({"error": "Invalid request"}, status=400)
