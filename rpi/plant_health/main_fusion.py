import os
import pickle
import torch
import torchvision.transforms as transforms
import numpy as np
import torchvision.models as models
import torch.nn as nn
from plant_health.sensor import SensorModel

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model_path = "plant_health/results/fusion.pkl"

# load image model
image_model_pth = 'plant_health/results/resnet.pth'
image_model = models.resnet18(pretrained=False)
num_features = image_model.fc.in_features
image_model.fc = nn.Linear(num_features, 2)
image_model.load_state_dict(torch.load(image_model_pth, map_location=DEVICE))
image_encoder = nn.Sequential(*list(image_model.children())[:-1]).to(DEVICE)
image_encoder.eval()
print("Successfully Loaded Image Model")

# load sensor model
sensor_model_pth = 'plant_health/results/sensor.pth'
sensor_encoder = SensorModel(input_dim=8).to(DEVICE)
sensor_encoder.load_state_dict(torch.load(sensor_model_pth, map_location=DEVICE))
sensor_encoder.eval()
print("Successfully Loaded Sensor Model")

# load fusion classifier
with open(model_path, 'rb') as f:
    fusion_model = pickle.load(f)

# resize to 224x224 - expected input size for models, ImageNet normalization
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

def health_check(image, sensor_data):
    image = transform(image)
    sensor_data = torch.tensor(sensor_data, dtype=torch.float32)
    image = image.unsqueeze(0).to(DEVICE)
    sensor = sensor_data.unsqueeze(0).to(DEVICE)
    print(f"image.shape: {image.shape}, sensor.shape: {sensor.shape}")
    
    # make sensor data match sensor model expected input
    if sensor.dim() == 2:  
        sensor = sensor.unsqueeze(1)
    
    # extract image features
    img_feat = image_encoder(image).squeeze()
    if img_feat.dim() == 1:
        img_feat = img_feat.unsqueeze(0)
    
    # extract sensor features 
    _, sensor_feat = sensor_encoder(sensor)
    if sensor_feat.dim() == 1:
        sensor_feat = sensor_feat.unsqueeze(0)
    
    print(f"img_feat.shape: {img_feat.shape}, sensor_feat.shape: {sensor_feat.shape}")
    
    # concatenate image and sensor features along dimension 1
    fused = torch.cat((img_feat, sensor_feat), dim=1)
    fused_feats = fused.detach().cpu().numpy()

    print(f"fused_feats.shape: {fused_feats.shape}")

    # classify into healthy or unhealthy
    pred = fusion_model.predict(fused_feats)
    pred = pred[0]
    print(f"pred.shape: {pred.shape}, pred: {pred}")

    health_status = "Healthy" if pred == 0 else "Unhealthy"
    
    return health_status
