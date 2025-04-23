import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.models as models
from plant_health.sensor import SensorModel

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class FusionModel(nn.Module):
    def __init__(self, image_model_pth, sensor_model_pth):
        super(FusionModel, self).__init__()

        image_model = models.resnet18(pretrained=False)
        num_features = image_model.fc.in_features
        image_model.fc = nn.Linear(num_features, 2)
        image_model.load_state_dict(torch.load(image_model_pth, map_location=DEVICE))
        self.image_encoder = nn.Sequential(*list(image_model.children())[:-1])

        sensor_encoder = SensorModel(input_dim=8)
        sensor_encoder.load_state_dict(torch.load(sensor_model_pth, map_location=DEVICE))
        self.sensor_encoder = sensor_encoder
    
    def forward(self, image, sensor):
        img_feat = self.image_encoder(image).squeeze()
        print(f"img_feat.shape: {img_feat.shape}")
        _, sensor_feat = self.sensor_encoder(sensor)
        sensor_feat = sensor_feat.squeeze()
        print(f"sensor_feat.shape: {sensor_feat.shape}")
        
        fused = torch.cat((img_feat, sensor_feat))
        return fused