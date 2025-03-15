from rest_framework import serializers
from .models import Plant, AutoSchedule

class PlantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plant
        fields = '__all__'
        
class AutoScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = AutoSchedule
        fields = '__all__'