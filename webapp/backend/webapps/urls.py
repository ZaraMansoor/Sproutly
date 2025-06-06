"""
URL configuration for webapps project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from sproutly.views import send_control_command, get_plant_species, get_webscraped_plant_data, add_user_plant, get_user_plants, get_sensor_data_history, get_plant_info, update_manual_autoschedule, change_automatic_or_manual, get_autoschedule, get_automatic_or_manual, change_number_of_plants, get_number_of_plants, get_detection_result, update_current_plant, get_current_plant, delete_plant


urlpatterns = [
    path('admin/', admin.site.urls),
    path('send-command/', send_control_command),
    path('get-user-plants/', get_user_plants),
    path('add-user-plant/', add_user_plant),
    path('manual-autoschedule/', update_manual_autoschedule),
    path("plant-species/", get_plant_species),
    path("get-plant-info/", get_plant_info),
    path("scrape-plant/", get_webscraped_plant_data),
    path('get-sensor-data-history/', get_sensor_data_history),
    path('get-autoschedule/<int:plant_id>/', get_autoschedule),
    path('automatic-or-manual/', change_automatic_or_manual),
    path('get-automatic-or-manual/', get_automatic_or_manual),
    path('change-number-of-plants/', change_number_of_plants),
    path('get-number-of-plants/', get_number_of_plants),
    path('get-detection-result/', get_detection_result),
    path('update-current-plant/', update_current_plant),
    path('get-current-plant/', get_current_plant),
    path('delete-plant/', delete_plant),
]
