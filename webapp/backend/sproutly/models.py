from django.db import models
from django.utils import timezone

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
    
    min_temp = models.FloatField(blank=True, null=True) # degree fahrenheit
    max_temp = models.FloatField(blank=True, null=True) # degree fahrenheit
    min_humidity = models.FloatField(blank=True, null=True) # %
    max_humidity = models.FloatField(blank=True, null=True) # %
    light_frequency = models.FloatField(blank=True, null=True) # hours
    light_hours = models.FloatField(blank=True, null=True) # hours
    water_frequency = models.FloatField(blank=True, null=True) # hours
    water_amount = models.IntegerField(blank=True, null=True) # mL

    # nutrients_target = models.FloatField(blank=True, null=True) # mL
    
    def __str__(self):
        return f"Auto schedule for {self.plant.name}"
    

class SensorData(models.Model):
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE, related_name='sensor_data', null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    temperature_c = models.FloatField(null=True, blank=True) # degree celsius
    temperature_f = models.FloatField(null=True, blank=True) # degree fahrenheit
    humidity = models.IntegerField(null=True, blank=True) # %

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
    water_description = models.CharField(max_length=100, blank=True, null=True) 
    temp_min = models.IntegerField(blank=True, null=True) # F
    temp_max = models.IntegerField(blank=True, null=True) # F
    humidity_min = models.IntegerField(blank=True, null=True) # %
    humidity_max = models.IntegerField(blank=True, null=True) # %

    def __str__(self):
        return f'Plant(name={self.name}, scientific_name={self.scientific_name})'
