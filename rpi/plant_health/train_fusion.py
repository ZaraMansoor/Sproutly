import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Subset
from torchvision import transforms
from tqdm import tqdm
import os
from dataset import FusionDataset
from fusion import FusionModel
from sklearn.model_selection import train_test_split
import pickle

BATCH_SIZE = 32
NUM_EPOCHS = 20
LEARNING_RATE = 1e-3
SENSOR_INPUT_DIM = 8
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
SAVE_PATH = 'results/fusion'
USE_VAL = True

os.makedirs(SAVE_PATH, exist_ok=True)

# resize to 224x224 - expected input size for models, ImageNet normalization
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

dataset = FusionDataset(
    csv_path='datasets/rpi/sensor_log.csv',
    image_dir='datasets/rpi/images',
    transform=transform,
    greyscale=False
)

labels = [sample[2] for sample in dataset]

train_val_idx, test_idx = train_test_split(
    list(range(len(dataset))),
    test_size=0.2,
    stratify=labels,
    random_state=42
)

if USE_VAL:
    val_ratio = 0.1
    train_idx, val_idx = train_test_split(
        train_val_idx,
        test_size=val_ratio,
        stratify=[labels[i] for i in train_val_idx],
        random_state=42
    )
    val_dataset = Subset(dataset, val_idx)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False)
else:
    train_idx = train_val_idx
    val_loader = None

train_dataset = Subset(dataset, train_idx)
test_dataset = Subset(dataset, test_idx)
train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False)

model = FusionModel('results/compare_models/plantdoc_dataset/ResNet18/best.pth', 'results/sensor/best.pth')
model = model.to(DEVICE)

# freeze image and sensor encoders
for param in model.image_encoder.parameters():
    param.requires_grad = False

for param in model.sensor_encoder.parameters():
    param.requires_grad = False


criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.fusion_head.parameters(), lr=LEARNING_RATE)
def evaluate(model, dataloader):
    model.eval()
    total = 0
    correct = 0
    with torch.no_grad():
        pbar = tqdm(iterable=dataloader)
        for images, sensors, labels in pbar:
            images = images.to(DEVICE)
            sensors = sensors.to(DEVICE)
            labels = labels.to(DEVICE)

            outputs = model(images, sensors)
            _, predicted = torch.max(outputs, 1)

            total += labels.size(0)
            correct += (predicted == labels).sum().item()
        pbar.close()

    return correct / total

def train():
    best_acc = 0.0
    best_model_path = os.path.join(SAVE_PATH, "best.pth")
    last_model_path = os.path.join(SAVE_PATH, "last.pth")

    for epoch in range(NUM_EPOCHS):
        model.train()
        epoch_loss = 0.0
        correct = 0
        total = 0

        pbar = tqdm(train_loader, desc=f"Epoch {epoch+1}/{NUM_EPOCHS}")
        for images, sensors, labels in pbar:
            images = images.to(DEVICE)
            sensors = sensors.to(DEVICE)
            labels = labels.to(DEVICE)

            optimizer.zero_grad()
            outputs = model(images, sensors)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            _, predicted = torch.max(outputs, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

            epoch_loss += loss.item()
            pbar.set_postfix(loss=loss.item())
        pbar.close()

        if val_loader:
            val_acc = evaluate(model, val_loader)
            print(f"Epoch {epoch+1} | Train Loss: {epoch_loss:.4f} | Val Acc: {val_acc:.4f}")
            if val_acc > best_acc:
                best_acc = val_acc
                torch.save(model.state_dict(), best_model_path)
                print(f"Best model saved at epoch {epoch+1} with val acc: {val_acc:.4f}")
        else:
            train_acc = correct / total
            print(f"Epoch {epoch+1} | Train Loss: {epoch_loss:.4f} | Train Acc: {train_acc:.4f}")
            if train_acc > best_acc:
                best_acc = train_acc
                torch.save(model.state_dict(), best_model_path)
                print(f"Best model saved at epoch {epoch+1} with train acc: {train_acc:.4f}")

    torch.save(model.state_dict(), last_model_path)
    print(f"Final model saved to {last_model_path}")


def save_test_dataset(test_dataset, file_path):
    test_data = []
    for i in range(len(test_dataset)):
        image, sensor, label = test_dataset[i]
        test_data.append({
            'image': image,
            'sensor': sensor,
            'label': label
        })
    
    with open(file_path, 'wb') as f:
        pickle.dump(test_data, f)
    print(f"Test dataset saved to {file_path}")


if __name__ == "__main__":
    train()
    save_test_dataset(test_dataset, file_path='datasets/rpi/test_dataset.pkl')