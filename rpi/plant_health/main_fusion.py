import torch
import torchvision.transforms as transforms
from fusion import FusionModel

# load model
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model_path = "plant_health/results/fusion/model.pth"
try:
    model = FusionModel('plant_health/results/resnet.pth', 'plant_health/results/sensor.pth')
    model.load_state_dict(torch.load(model_path))
    model.to(device)
    model.eval()
except FileNotFoundError:
    print(f"Error: Model file '{model_path}' not found. Returning default status.")
    model = None

def health_check(image, sensor_data):
    if model is None:
        return "Unknown"
    
    model.eval()

    # resize to 224x224 - expected input size for models, ImageNet normalization
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    # transform image
    image_tensor = transform(image).unsqueeze(0).to(device)
    sensor_tensor = torch.tensor(sensor_data, dtype=torch.float).unsqueeze(0).to(device)

    # evaluate image
    with torch.no_grad():
        outputs = model(image_tensor, sensor_tensor)
        _, pred = torch.max(outputs, 1)

    pred = pred.cpu().numpy()[0]
    health_status = "Healthy" if pred == 0 else "Unhealthy"
    
    return health_status
