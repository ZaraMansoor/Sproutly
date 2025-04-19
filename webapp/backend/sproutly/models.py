from django.db import models
from django.utils import timezone
import datetime

class Plant(models.Model): # user's plant
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    species = models.CharField(max_length=100)
    image_url = models.URLField(blank=True, null=True)
    health_status = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f'Plant(name={self.name}, species={self.species}, health_status="{self.health_status}")'


class AutoSchedule(models.Model):
    plant = models.OneToOneField(Plant, on_delete=models.CASCADE, related_name='auto_schedule')

    automatic_mode = models.BooleanField(default=True)
    # TODO: change to blank=False and null=False later!
    number_of_plants = models.IntegerField(default=1,blank=True, null=True) # 1, 2, or 3
    
    min_temp = models.FloatField(blank=True, null=True) # degree fahrenheit
    max_temp = models.FloatField(blank=True, null=True) # degree fahrenheit
    min_humidity = models.FloatField(blank=True, null=True) # %
    max_humidity = models.FloatField(blank=True, null=True) # %
    light_start_time = models.TimeField(default=datetime.time(9, 0), null=True, blank=True) # default: 9am
    light_intensity = models.IntegerField(blank=True, null=True) # 1, 2, 3, or 4
    light_hours = models.FloatField(default=9, blank=True, null=True) # hours (duration), default: 9 hours
    water_frequency = models.FloatField(default=7, blank=True, null=True) # days
    water_start_time = models.TimeField(default=datetime.time(9, 0), null=True, blank=True) # default: 9am
    water_amount = models.IntegerField(default=100,blank=True, null=True) # mL, default: 100mL
    nutrients_start_time = models.TimeField(default=datetime.time(9, 0), null=True, blank=True) # default: 9am
    nutrients_amount = models.IntegerField(default=2, blank=True, null=True) # mL, default: 2mL per 100mL water

    
    def __str__(self):
        return f"Auto schedule for {self.plant.name}"
    

class SensorData(models.Model):
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE, related_name='sensor_data', null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    temperature_c = models.FloatField(null=True, blank=True) # degree celsius
    temperature_f = models.FloatField(null=True, blank=True) # degree fahrenheit
    humidity = models.IntegerField(null=True, blank=True) # %
    soil_moisture = models.FloatField(null=True, blank=True) # %
    lux = models.IntegerField(null=True, blank=True) # lux
    ph = models.FloatField(null=True, blank=True) # pH
    soil_temp = models.FloatField(null=True, blank=True) # degree celsius
    conductivity = models.FloatField(null=True, blank=True) # uS/cm
    nitrogen = models.FloatField(null=True, blank=True) # mg/kg
    phosphorus = models.FloatField(null=True, blank=True) # mg/kg
    potassium = models.FloatField(null=True, blank=True) # mg/kg

    def __str__(self):
        return f"Sensor data for {self.plant.name}: temperature_c={self.temperature_c}, temperature_f={self.temperature_f}, humidity={self.humidity}"


class WebscrapedPlant(models.Model):
    index = models.IntegerField()
    name = models.CharField(max_length=100)
    image_url = models.URLField()
    info_url = models.URLField() # link

    # web scraped data
    scientific_name = models.CharField(max_length=100, blank=True, null=True)
    light_description = models.CharField(max_length=100, blank=True, null=True)
    light_t0 = models.IntegerField(blank=True, null=True)
    light_duration = models.IntegerField(blank=True, null=True)
    light_intensity = models.IntegerField(blank=True, null=True)
    water_description = models.CharField(max_length=3000, blank=True, null=True) 
    temp_min = models.IntegerField(blank=True, null=True) # F
    temp_max = models.IntegerField(blank=True, null=True) # F
    humidity_min = models.IntegerField(blank=True, null=True) # %
    humidity_max = models.IntegerField(blank=True, null=True) # %
    ph_min = models.FloatField(blank=True, null=True) # pH
    ph_max = models.FloatField(blank=True, null=True) # pH

    def __str__(self):
        return f'Plant(name={self.name}, scientific_name={self.scientific_name})'


class PlantDetectionData(models.Model):
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE, related_name='plant_detection_data', null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    best_match = models.CharField(max_length=100, blank=False, null=False)
    common_names = models.JSONField(default=list, blank=False, null=False)

    def __str__(self):
        return f"Plant detection data for {self.plant.name}: best_match={self.best_match}, common_names={self.common_names}"
