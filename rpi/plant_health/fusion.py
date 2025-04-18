import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.models as models
from sensor import SensorModel

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class FusionHead(nn.Module):
    def __init__(self, input_dim):
        super(FusionHead, self).__init__()
        self.fc1 = nn.Linear(input_dim, 512)
        self.fc2 = nn.Linear(512, 128)
        self.fc3 = nn.Linear(128, 2)

        self.dropout = nn.Dropout(p=0.5)
    
    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = self.dropout(x)

        x = F.relu(self.fc2(x))
        x = self.dropout(x)

        x = self.fc3(x)
        return x

class FusionModel(nn.Module):
    def __init__(self, image_model_pth, sensor_model_pth):
        super(FusionModel, self).__init__()

        image_model = models.resnet18(pretrained=False)
        num_features = image_model.fc.in_features
        image_model.fc = nn.Linear(num_features, 2)
        image_model.load_state_dict(torch.load(image_model_pth, map_location=DEVICE))
        self.image_encoder = nn.Sequential(*list(image_model.children())[:-1])

        sensor_encoder = SensorModel()
        sensor_encoder.load_state_dict(torch.load(sensor_model_pth, map_location=DEVICE))
        self.sensor_encoder = sensor_encoder
        
        self.fusion_head = FusionHead(512 + 128)
    
    def forward(self, image, sensor):
        img_feat = self.image_encoder(image).squeeze()
        _, sensor_feat = self.sensor_encoder(sensor)
        
        fused = torch.cat((img_feat, sensor_feat), dim=1)
        return self.fusion_head(fused)