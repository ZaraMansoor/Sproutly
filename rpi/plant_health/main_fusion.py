import os
import pickle
import torch
import torchvision.transforms as transforms
from plant_health.fusion import FusionModel
import numpy as np

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model_path = "plant_health/results/fusion.pkl"

# load model
model = FusionModel('plant_health/results/resnet.pth', 'plant_health/results/sensor.pth')
model.to(device)

with open(model_path, 'rb') as f:
    fusion_model = pickle.load(f)

# resize to 224x224 - expected input size for models, ImageNet normalization
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])


def health_check(image, sensor_data):
    sensor_data = np.array(sensor_data)
    model.eval()

    # transform image
    image_tensor = transform(image).unsqueeze(0).to(device)
    sensor_tensor = torch.tensor(sensor_data, dtype=torch.float).unsqueeze(0).to(device)

    print(f"image_tensor.shape: {image_tensor.shape}, sensor_tensor.shape: {sensor_tensor.shape}")

    # find the concatenated sensor and image features
    with torch.no_grad():
        fused = model(image_tensor, sensor_tensor)
        print(f"fused.shape: {fused.shape}")
        fused = fused.cpu().numpy()
    
    # classify into healthy or unhealthy
    pred = fusion_model.predict(fused)
    pred = pred[0]
    print(f"pred.shape: {pred.shape}, pred: {pred}")

    health_status = "Healthy" if pred == 0 else "Unhealthy"
    
    return health_status
