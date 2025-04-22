import requests
import os
import csv

API_KEY = "2b10KGTzAgqcb5baVQciCheRU"  # Set your API_KEY here
PROJECT = "all"  # try "weurope" or "canada"
api_endpoint = f"https://my-api.plantnet.org/v2/identify/{PROJECT}?api-key={API_KEY}"

def identify_plant(image_path):
    image_data = open(image_path, 'rb')
    files = [
        ('images', (image_path, image_data))
    ]

    response = requests.post(api_endpoint, files=files)
    json_result = response.json()
    if response.status_code == 200:
        best_match = json_result.get("bestMatch", "Unknown")
        common_names = json_result["results"][0]["species"].get("commonNames", [])
        return best_match, common_names
    if response.status_code == 429:
        print("API rate limit reached. Stopping execution.")
        return "RATE_LIMIT_REACHED", []

# path to .csv
csv_path = 'datasets/rpi/sensor_log.csv'
image_folder = 'datasets/rpi/images'
output_csv_path = 'datasets/rpi/plant_id_results.csv'
start_row = 395

with open(csv_path, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for i, row in enumerate(reader):
        if i < start_row:
            continue

        image_path = os.path.join(image_folder, row['Image Path'])
        if os.path.exists(image_path):
            actual = row['Plant Species']
            best_match, common_names = identify_plant(image_path)

            if best_match == "RATE_LIMIT_REACHED":
                break

            with open(output_csv_path, mode='a', newline='') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=['actual', 'best_match', 'common_names'])
                writer.writerow({
                    'actual': actual,
                    'best_match': best_match,
                    'common_names': ", ".join(common_names)
                })
        else:
            print(f"Image not found: {image_path}")

print(f"Results saved incrementally to {output_csv_path}")