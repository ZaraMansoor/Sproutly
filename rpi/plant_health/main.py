import io
import time
import torch
import torchvision.transforms as transforms
import matplotlib.pyplot as plt
from PIL import Image
from picamera2 import Picamera2
from torchvision import models
from torch import nn

# load pretrained models
def load_model(model_name='resnet18'):
    if model_name == 'resnet18':
        model = models.resnet18(pretrained=False)
    elif model_name == 'resnet50':
        model = models.resnet50(pretrained=False)
    elif model_name == 'mobilenet_v2':
        model = models.mobilenet_v2(pretrained=False)
    
    # modify the last layer for binary classification
    num_features = model.fc.in_features if 'resnet' in model_name else model.classifier[1].in_features
    if 'resnet' in model_name:
        model.fc = nn.Linear(num_features, 2)
    else:
        model.classifier[1] = nn.Linear(num_features, 2)

    return model

def health_check():
    # capture image 
    picam2 = Picamera2()
    picam2.start()
    time.sleep(2)

    image_stream = io.BytesIO()
    picam2.capture_file(image_stream, format="jpeg")
    image_stream.seek(0)

    image = Image.open(image_stream)

    plt.imshow(image)
    plt.axis('off')
    plt.title("Captured Image")
    plt.show()

    # resize to 224x224 - expected input size for models, ImageNet normalization
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    # convert image stream to PIL image
    image = Image.open(image_stream)
    image = transform(image).unsqueeze(0)

    # load model
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model_path = "plant_health/results/model.pth"

    try:
        model = load_model('resnet18')
        model.load_state_dict(torch.load(model_path, map_location=device))
        model.to(device)
        model.eval()

        # evaluate image
        with torch.no_grad():
            image = image.to(device)
            outputs = model(image)
            _, pred = torch.max(outputs, 1)

        pred = pred.cpu().numpy()[0]
        health_status = "Healthy" if pred == 0 else "Unhealthy"

    except FileNotFoundError:
        print(f"Error: Model file '{model_path}' not found. Returning default status.")
        health_status = "Unknown"

    return health_status
