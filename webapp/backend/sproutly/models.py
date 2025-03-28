from django.db import models
from django.utils import timezone

class Plant(models.Model):
    name = models.CharField(max_length=100)
    species = models.CharField(max_length=100)
    image = models.ImageField(upload_to='plant_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    health_status = models.CharField(max_length=100)
    # TODO: add more sensor data 

    def __str__(self):
        return f'Plant(name={self.name}, species={self.species}, health_status="{self.health_status}")'


class AutoSchedule(models.Model):
    plant = models.OneToOneField(Plant, on_delete=models.CASCADE, related_name='auto_schedule')
    
    watering_enabled = models.BooleanField(default=True)
    watering_amount = models.FloatField() # mL
    
    humidity_control_enabled = models.BooleanField(default=True)
    humidity_target = models.FloatField() # %
    
    lighting_enabled = models.BooleanField(default=True)
    lighting_hours = models.IntegerField() # hours/day
    
    temperature_control_enabled = models.BooleanField(default=True)
    temperature_target = models.FloatField() # degree celsius

    nutrients_control_enabled = models.BooleanField(default=True)
    nutrients_target = models.FloatField() # mL
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Auto schedule for {self.plant.name}"
    

class SensorData(models.Model):
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE, related_name='sensor_data')

    def __str__(self):
        return f"Sensor data for {self.plant.name}"


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
