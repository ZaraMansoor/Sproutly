import os
import pickle
import pandas as pd
import torch
from torch.utils.data import Dataset
from PIL import Image
from sklearn.model_selection import train_test_split

# image dataset
class ImageDataset(Dataset):
    def __init__(self, dataset_path, transform=None, greyscale=False, multi_class_labels=None):
        '''
        Args:
            dataset_path (str): Path to the pickle file containing the dataset.
            transform (callable, optional): Optional transform to be applied on an image.
            grayscale (bool): Flag to convert images to grayscale but keep 3 channels.
        '''

        # open and load the dataset from the pickle file
        with open(dataset_path, 'rb') as f:
            dataset = pickle.load(f)

        self.dataset = dataset
        self.transform = transform
        self.greyscale = greyscale
        self.multi_class_labels = multi_class_labels
        print(f'multi_class_labels: {multi_class_labels}, num_classes: {len(multi_class_labels)}')

    def __len__(self):
        return len(self.dataset)

    def __getitem__(self, idx):
        '''
        Args:
            idx (int): Index of the data sample.
        
        Returns:
            image: Transformed image tensor 
            health_class: Binary health class (0: healthy, 1: unhealthy)
        '''
        sample = self.dataset[idx]
        image_path = sample['image_path']
        image = Image.open(image_path).convert('RGB')

        # convert to greyscale but still keep 3 channels
        if self.greyscale:
            image = image.convert('L')
            image = image.convert('RGB')

        if not self.multi_class_labels:
            # convert the health label to a binary class (healthy/unhealthy)
            # 0 : healthy and 1 : unhealthy
            health_class = 0 if sample['health_class'] == 'healthy' else 1  
        else:
            # convert the health labels to indices
            if sample['health_class'] == 'healthy':
                health_class = self.multi_class_labels.index('healthy')
            else:
                label = sample['health_labels'].split(', ')[0]
                health_class = self.multi_class_labels.index(label)

        # apply transformations if provided
        if self.transform:
            image = self.transform(image)

        return image, health_class

# sensor dataset
class SensorDataset(Dataset):
    def __init__(self, dataset_path):
        '''
        Args:
            dataset_path (str): Path to the CSV file containing the dataset.
        '''

        # load the dataset
        df = pd.read_csv(dataset_path)

        # extract features
        self.features = df.drop(columns=['Timestamp', 
                                         'Plant_ID', 
                                         'Soil_Temperature',
                                         'Plant_Health_Status', 
                                         'Chlorophyll_Content', 
                                         'Electrochemical_Signal'])
        
        # make health labels binary
        self.health_class = df['Plant_Health_Status'].apply(lambda x: 0 if x.lower() == 'healthy' else 1)

    def __len__(self):
        return len(self.features)

    def __getitem__(self, idx):
        '''
        Args:
            idx (int): Index of the data sample.
        
        Returns:
            data: Tensor containing features of the sensor data
            health_class: Binary health class (0: healthy, 1: unhealthy)
        '''
        data = self.features.iloc[idx].values
        health_class = self.health_class.iloc[idx]

        data = torch.tensor(data, dtype=torch.float32)
        health_class = torch.tensor(health_class, dtype=torch.long)

        return data, health_class

# split into train, test, and optionally val
def split_dataset(dataset, val=False, val_size=0.15, test_size=0.1, random_seed=42):
    # split into train and test
    labels = [health_class for _, health_class in dataset]
    train_dataset, test_dataset = train_test_split(dataset, test_size=test_size, random_state=random_seed, stratify=labels)
    
    if (val):
        # split train into train and val
        train_labels = [health_class for _, health_class in train_dataset]
        train_dataset, val_dataset = train_test_split(train_dataset, test_size=val_size, random_state=random_seed, stratify=train_labels)
    else:
        val_dataset = None
    
    return train_dataset, val_dataset, test_dataset



class FusionDataset(Dataset):
    def __init__(self, csv_path, image_dir, transform=None, greyscale=False):
        df = pd.read_csv(csv_path)
        self.image_dir = image_dir
        self.transform = transform
        self.greyscale = greyscale

        # change column names to match online sensor data columns
        df = df.rename(columns={
            'Soil Moisture (%)': 'Soil_Moisture',
            'Temperature (°C)': 'Ambient_Temperature',
            'Humidity (%)': 'Humidity',
            'Light (lux)': 'Light_Intensity',
            'Soil pH': 'Soil_pH',
            'Nitrogen (mg/kg)': 'Nitrogen_Level',
            'Phosphorus (mg/kg)': 'Phosphorus_Level',
            'Potassium (mg/kg)': 'Potassium_Level',
            'Health': 'Plant_Health_Status',
            'Image Path': 'image_path'
        })

        # make health labels binary
        self.health_class = df['Plant_Health_Status'].apply(lambda x: 0 if str(x).strip().lower() == 'healthy' else 1)

        # extract features
        self.sensor_columns = [
            'Soil_Moisture',
            'Ambient_Temperature',
            'Humidity',
            'Light_Intensity',
            'Soil_pH',
            'Nitrogen_Level',
            'Phosphorus_Level',
            'Potassium_Level'
        ]

        self.features = df[self.sensor_columns]
        self.image_paths = df['image_path']
        self.plant_species = df['Plant Species']
        self.plant_ids = df['Plant ID']

    def __len__(self):
        return len(self.features)

    def __getitem__(self, idx):
        sample = self.features.iloc[idx]

        # load and transform image
        image_path = os.path.join(self.image_dir, self.image_paths.iloc[idx])
        image = Image.open(image_path).convert('RGB')

        # convert to greyscale but still keep 3 channels
        if self.greyscale:
            image = image.convert('L')
            image = image.convert('RGB')

        # apply transformations if provided
        if self.transform:
            image = self.transform(image)

        # sensor features
        sensor_data = torch.tensor(sample.values, dtype=torch.float32)
        health_class = torch.tensor(self.health_class.iloc[idx], dtype=torch.long)
        plant_species = self.plant_species.iloc[idx]
        plant_ids = self.plant_ids.iloc[idx]

        return image, sensor_data, health_class, plant_species, plant_ids
