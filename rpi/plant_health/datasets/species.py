import pandas as pd

csv_path = 'rpi/sensor_log.csv'
df = pd.read_csv(csv_path)

def get_plant_species(image_name):
    number = int(image_name.split('_')[1].split('.')[0])
    if 0 <= number <= 95:
        return 'Snake Plant'
    elif 96 <= number <= 237:
        return 'African Violet'
    elif 238 <= number <= 361:
        return 'Peperomia'
    elif 362 <= number <= 483:
        return 'African Violet'
    elif 484 <= number <= 563:
        return 'Peperomia'
    elif 564 <= number:
        return 'Hedera Ivy'

df['Plant Species'] = df['Image Path'].apply(get_plant_species)
df.to_csv('rpi/updated_sensor_log.csv', index=False)
