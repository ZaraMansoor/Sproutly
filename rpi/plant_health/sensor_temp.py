import os
import torch
import torch.nn as nn
import numpy as np
from dataset import SensorDataset
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, classification_report
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from torch.utils.data import DataLoader, TensorDataset
import torch.optim as optim
from sklearn.utils.class_weight import compute_class_weight
from xgboost import XGBClassifier
import joblib

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f'torch.cuda.is_available(): {torch.cuda.is_available()}')
print(f'device: {device}')

# function to train sensor model
def train():
    # load and split dataset
    dataset_path = 'datasets/sensor_data.csv'
    dataset = SensorDataset(dataset_path=dataset_path)
    
    features = np.array([item[0].numpy() for item in dataset])
    labels = np.array([item[1].item() for item in dataset])
    train_X, test_X, train_y, test_y = train_test_split(features, labels, test_size=0.1, random_state=42, stratify=labels)

    xgb = XGBClassifier(scale_pos_weight=np.bincount(train_y)[0] / np.bincount(train_y)[1])
    xgb.fit(train_X, train_y)

    # save model
    output_dir = 'results/sensor'
    os.makedirs(output_dir, exist_ok=True)
    model_path = os.path.join(output_dir, 'sensor_model.joblib')
    joblib.dump(xgb, model_path)
    print(f'Model saved to {model_path}')

    # evaluate
    preds = xgb.predict(test_X)

    with open(os.path.join(output_dir, 'results.txt'), 'w') as f:
        f.write("Sensor Model Evaluation Results:\n\n\n")

        target_names = ['healthy', 'unhealthy']
        classification_rep = classification_report(test_y, preds, target_names=target_names)
        
        conf_matrix = confusion_matrix(test_y, preds)
        conf_matrix_df = pd.DataFrame(conf_matrix, 
                                    index=['Actual Healthy', 'Actual Unhealthy'], 
                                    columns=['Predicted Healthy', 'Predicted Unhealthy'])

        # save the confusion matrix as an image to the output directory
        plt.figure(figsize=(8, 6))
        sns.heatmap(conf_matrix_df, annot=True, fmt='g', cmap='Blues', xticklabels=target_names, yticklabels=target_names)
        plt.title('Confusion Matrix:')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')

        image_file = os.path.join(output_dir, 'confusion_matrix.png')
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
                    
        norm_image_file = os.path.join(output_dir, 'normalized_confusion_matrix.png')
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
        
        print(f'Results saved to {output_dir}/results.txt')
        

if __name__ == '__main__':
    train()
