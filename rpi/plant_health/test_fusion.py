import os
import torch
import pickle
import csv
import matplotlib.pyplot as plt
import numpy as np
from fusion import FusionModel
from torch.utils.data import DataLoader, TensorDataset
from tqdm import tqdm
from sklearn.metrics import confusion_matrix, classification_report
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

BATCH_SIZE = 32
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

def load_model(model_path):
    model = FusionModel('results/compare_models/plantdoc_dataset/ResNet18/best.pth', 'results/sensor/best.pth')
    model.load_state_dict(torch.load(model_path))
    model.eval()
    return model

def test(model, test_data, device):
    test_loader = DataLoader(test_data, batch_size=BATCH_SIZE, shuffle=False)

    predictions = []
    true_labels = []
    
    with torch.no_grad():
        for images, sensors, labels in tqdm(test_loader, desc="Testing"):
            images = images.to(device)
            sensors = sensors.to(device)
            labels = labels.to(device)

            outputs = model(images, sensors)
            _, predicted = torch.max(outputs, 1)
            
            predictions.extend(predicted.cpu().numpy())
            true_labels.extend(labels.cpu().numpy())

    return predictions, true_labels

def save_predictions(predictions, true_labels, file_path):
    with open(file_path, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['True Label', 'Prediction'])
        for true, pred in zip(true_labels, predictions):
            writer.writerow([true, pred])
    print(f"Predictions saved to {file_path}")

def load_test_dataset(file_path='datasets/rpi/test_dataset.pkl'):
    with open(file_path, 'rb') as f:
        test_data = pickle.load(f)

    images = [sample['image'] for sample in test_data]
    sensors = [sample['sensor'] for sample in test_data]
    labels = [sample['label'] for sample in test_data]

    images_tensor = torch.stack(images)
    sensors_tensor = torch.stack(sensors)
    labels_tensor = torch.tensor(labels)

    test_tensor_dataset = TensorDataset(images_tensor, sensors_tensor, labels_tensor)
    return test_tensor_dataset

def plot_confusion_matrix(cm, labels, normalize=False, file_path='confusion_matrix.png'):
    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]

    plt.figure(figsize=(6, 6))
    plt.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
    plt.title('Confusion Matrix')
    plt.colorbar()
    tick_marks = np.arange(len(labels))
    plt.xticks(tick_marks, labels, rotation=45)
    plt.yticks(tick_marks, labels)

    plt.ylabel('True label')
    plt.xlabel('Predicted label')
    plt.tight_layout()

    plt.savefig(file_path)
    plt.close()

def save_metrics(preds, labels, file_path):
    with open(os.path.join(file_path, 'results.txt'), 'w') as f:
        target_names = ['healthy', 'unhealthy']
        classification_rep = classification_report(labels, preds, target_names=target_names)

        conf_matrix = confusion_matrix(labels, preds)
        conf_matrix_df = pd.DataFrame(conf_matrix, 
                                    index=['Actual Healthy', 'Actual Unhealthy'], 
                                    columns=['Predicted Healthy', 'Predicted Unhealthy'])

        # save the confusion matrix as an image to the output directory
        plt.figure(figsize=(8, 6))
        sns.heatmap(conf_matrix_df, annot=True, fmt='g', cmap='Blues', xticklabels=target_names, yticklabels=target_names)
        plt.title('Confusion Matrix:')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')

        image_file = os.path.join(file_path, 'confusion_matrix.png')
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
                
        norm_image_file = os.path.join(file_path, 'normalized_confusion_matrix.png')
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
        
        print(f"Metrics saved to {file_path}")

if __name__ == "__main__":
    # Load test dataset
    test_dataset = load_test_dataset('datasets/rpi/test_dataset.pkl')

    # Load trained model
    model = load_model('results/fusion/best.pth')
    model = model.to(DEVICE)

    # Perform the test and get predictions
    predictions, true_labels = test(model, test_dataset, DEVICE)

    # Save predictions to a CSV file
    save_predictions(predictions, true_labels, 'results/fusion/test_predictions.csv')
    save_metrics(predictions, true_labels, 'results/fusion')
