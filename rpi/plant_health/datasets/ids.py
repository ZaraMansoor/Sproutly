import pandas as pd

csv_path = 'rpi/sensor_log.csv'
df = pd.read_csv(csv_path)

def get_plant_species(image_name):
    number = int(image_name.split('_')[1].split('.')[0])
    if 0 <= number <= 80:
        return 'Snake Plant Healthy 1'
    elif 81 <= number <= 95:
        return 'Snake Plant Healthy 2'
    elif 96 <= number <= 150:
        return 'African Violet Unhealthy 1'
    elif 151 <= number <= 167:
        return 'African Violet Unhealthy 2'
    elif 168 <= number <= 237:
        return 'African Violet Unhealthy 3'
    elif 238 <= number <= 321:
        return 'Peperomia Unhealthy 1'
    elif 322 <= number <= 361:
        return 'Peperomia Unhealthy 2'
    elif 362 <= number <= 425:
        return 'African Violet Healthy 1'
    elif 426 <= number <= 483:
        return 'African Violet Healthy 2'
    elif 484 <= number <= 534:
        return 'Peperomia Healthy 1'
    elif 535 <= number <= 563:
        return 'Peperomia Healthy 2'
    elif 564 <= number <= 588:
        return 'Hedera Ivy Healthy 1'
    else:
        return 'Unknown'

df['Plant ID'] = df['Image Path'].apply(get_plant_species)
df.to_csv('rpi/updated_sensor_log.csv', index=False)
