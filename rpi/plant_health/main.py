import io
import time
import torch
import torchvision.transforms as transforms
from PIL import Image
from picamera2 import Picamera2

def health_check():
    # capture image 
    picam2 = Picamera2()
    picam2.start()
    time.sleep(2)

    image_stream = io.BytesIO()
    picam2.capture_file(image_stream, format="jpeg")
    image_stream.seek(0)

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
    model_path = "results/model.pth"
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    try:
        model = torch.load(model_path, map_location=device)
        model.eval()
        model.to(device)

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
