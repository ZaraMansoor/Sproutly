import os
import torch
import torch.nn as nn
import torchvision.models as models
from sensor import SensorModel
from torch.utils.data import DataLoader, Subset
from torchvision import transforms
from dataset import FusionDataset
from sklearn.model_selection import train_test_split
import numpy as np
import pickle
from xgboost import XGBClassifier
from sklearn.metrics import classification_report, confusion_matrix
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"torch.cuda.is_available(): {torch.cuda.is_available()}")
print(f"device: {DEVICE}")

BATCH_SIZE = 32
OUTPUT_DIR = 'results/fusion_id_3'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# load image model
image_model_pth = 'results/compare_models/plantdoc_dataset/ResNet18/best.pth'
image_model = models.resnet18(pretrained=False)
num_features = image_model.fc.in_features
image_model.fc = nn.Linear(num_features, 2)
image_model.load_state_dict(torch.load(image_model_pth, map_location=DEVICE))
image_encoder = nn.Sequential(*list(image_model.children())[:-1]).to(DEVICE)
image_encoder.eval()
print("Successfully Loaded Image Model")

# load sensor model
sensor_model_pth = 'results/sensor/sensor_model.pth'
sensor_encoder = SensorModel(input_dim=8).to(DEVICE)
sensor_encoder.load_state_dict(torch.load(sensor_model_pth, map_location=DEVICE))
sensor_encoder.eval()
print("Successfully Loaded Sensor Model")

# feature extraction
def extract_fused_features(dataloader):
    fused_feats = []
    all_labels = []
    with torch.no_grad():
        for batch in dataloader:
            image, sensor, labels, _, _ = batch 
            image = image.to(DEVICE)
            sensor = sensor.to(DEVICE)
            labels = labels.to(DEVICE)
            
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
            
            # concatenate image and sensor features along dimension 1
            fused = torch.cat((img_feat, sensor_feat), dim=1)
            fused_feats.append(fused.cpu().numpy())
            all_labels.append(labels.cpu().numpy())

    # combine all batches
    print("Successfully Extracted Features")
    return np.concatenate(fused_feats, axis=0), np.concatenate(all_labels, axis=0)


def build_fused_datasets():
    csv_path = 'datasets/rpi/updated_sensor_log.csv'
    image_dir = 'datasets/rpi/images'
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    dataset = FusionDataset(csv_path=csv_path, image_dir=image_dir, transform=transform, greyscale=False)

    # split based on plant id
    train_indices = []
    test_indices = []
    for idx in range(len(dataset)):
        _, _, _, _, plant_ids = dataset[idx]
        if str(plant_ids) in ['Snake Plant Healthy 2', 'African Violet Unhealthy 3', 
                              'Peperomia Unhealthy 2', 'African Violet Healthy 2', 
                              'Peperomia Healthy 2']:
            test_indices.append(idx)
        else:
            train_indices.append(idx)

    print(f"Train size: {len(train_indices)}, Test size: {len(test_indices)}")

    train_dataset = Subset(dataset, train_indices)
    test_dataset = Subset(dataset, test_indices)

    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False)

    # extract fused features from both train and test loaders
    train_fused_feats, train_labels = extract_fused_features(train_loader)
    test_fused_feats, test_labels = extract_fused_features(test_loader)
    
    print("Successfully Built Dataset (Species Split)")
    return train_fused_feats, train_labels, test_fused_feats, test_labels


# save the datasets as .pkl files
def save_fused_datasets():
    train_path = os.path.join(OUTPUT_DIR, 'train_dataset.pkl')
    test_path = os.path.join(OUTPUT_DIR, 'test_dataset.pkl')

    if os.path.exists(train_path) and os.path.exists(test_path):
        print("Fused datasets found. Loading...")
        with open(train_path, 'rb') as f:
            train_data = pickle.load(f)
        with open(test_path, 'rb') as f:
            test_data = pickle.load(f)
    else:
        print("No datasets found. Building from scratch...")
        train_feats, train_labels, test_feats, test_labels = build_fused_datasets()

        with open(train_path, 'wb') as f:
            pickle.dump({'features': train_feats, 'labels': train_labels}, f)
        with open(test_path, 'wb') as f:
            pickle.dump({'features': test_feats, 'labels': test_labels}, f)
        print("Fused datasets saved.")

        train_data = {'features': train_feats, 'labels': train_labels}
        test_data = {'features': test_feats, 'labels': test_labels}

    return train_data['features'], train_data['labels'], test_data['features'], test_data['labels']


# train a classifier
def train(X_train, y_train, X_test, y_test):
    print("Entered Training")
    # train
    class_weights = np.bincount(y_train)
    scale_pos_weight = class_weights[0] / class_weights[1] if class_weights[1] > 0 else 1
    model = XGBClassifier(use_label_encoder=False, eval_metric='logloss', scale_pos_weight=scale_pos_weight)
    model.fit(X_train, y_train)
    
    # save the trained model
    model_path = os.path.join(OUTPUT_DIR, 'xgb_model.pkl')
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    print(f"Trained XGBoost model saved to {model_path}")

    print("Successfully Trained Classifier")

    # evaluate
    y_pred = model.predict(X_test)
    print("Successfully Predicted, Compiling Metrics Now...")

    # save results
    with open(os.path.join(OUTPUT_DIR, 'results.txt'), 'w') as f:
        target_names = ['healthy', 'unhealthy']
        classification_rep = classification_report(y_test, y_pred, target_names=target_names)

        conf_matrix = confusion_matrix(y_test, y_pred)
        conf_matrix_df = pd.DataFrame(conf_matrix, 
                                    index=['Actual Healthy', 'Actual Unhealthy'], 
                                    columns=['Predicted Healthy', 'Predicted Unhealthy'])

        # save the confusion matrix as an image to the output directory
        plt.figure(figsize=(8, 6))
        sns.heatmap(conf_matrix_df, annot=True, fmt='g', cmap='Blues', xticklabels=target_names, yticklabels=target_names)
        plt.title('Confusion Matrix:')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')

        image_file = os.path.join(OUTPUT_DIR, 'confusion_matrix.png')
        os.makedirs(os.path.dirname(image_file), exist_ok=True)
        plt.savefig(image_file)
        plt.close()

        # save the normalised confusion matrix as an image to the output directory
        normalised_conf_matrix = conf_matrix.astype('float') / conf_matrix.sum(axis=1)[:, np.newaxis]
        normalised_conf_matrix_df = pd.DataFrame(normalised_conf_matrix, 
                                                    index=['Actual Healthy', 'Actual Unhealthy'], 
                                                    columns=['Predicted Healthy', 'Predicted Unhealthy'])
        plt.figure(figsize=(8, 6))
        sns.heatmap(normalised_conf_matrix_df, annot=True, fmt='.2f', cmap='Blues', xticklabels=target_names, yticklabels=target_names)
        plt.title('Normalized Confusion Matrix:')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
                
        norm_image_file = os.path.join(OUTPUT_DIR, 'normalized_confusion_matrix.png')
        os.makedirs(os.path.dirname(norm_image_file), exist_ok=True)
        plt.savefig(norm_image_file)
        plt.close()

        # calculate metrics
        tn, fp, fn, tp = conf_matrix.ravel()
        tpr = tp / (tp + fn)
        tnr = tn / (tn + fp)
        fpr = fp / (fp + tn)
        fnr = fn / (fn + tp)

        f.write(f'Evaluation Results:\n{classification_rep}\n')
        f.write(f'Confusion Matrix:\n{conf_matrix_df.to_string()}\n\n')
        f.write(f'True Positive Rate (TPR): {tpr:.4f}\n')
        f.write(f'True Negative Rate (TNR): {tnr:.4f}\n')
        f.write(f'False Positive Rate (FPR): {fpr:.4f}\n')
        f.write(f'False Negative Rate (FNR): {fnr:.4f}\n\n')

        print(classification_rep)
        print(f'Confusion Matrix:\n{conf_matrix_df}')
        print(f'True Positive Rate (TPR): {tpr:.4f}')
        print(f'True Negative Rate (TNR): {tnr:.4f}')
        print(f'False Positive Rate (FPR): {fpr:.4f}')
        print(f'False Negative Rate (FNR): {fnr:.4f}\n')
        
        print(f"Metrics saved to {OUTPUT_DIR}")

if __name__ == "__main__":
    train_feats, train_labels, test_feats, test_labels = save_fused_datasets()
    train(train_feats, train_labels, test_feats, test_labels)

