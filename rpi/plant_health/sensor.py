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


device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f'torch.cuda.is_available(): {torch.cuda.is_available()}')
print(f'device: {device}')

# class SensorModel(nn.Module):
#     def __init__(self, input_dim, output_dim=128):
#         super(SensorModel, self).__init__()
#         self.layer1 = nn.Linear(input_dim, 64)
#         self.relu = nn.ReLU()
#         self.layer2 = nn.Linear(64, output_dim)
#         self.layer3 = nn.Linear(output_dim, 1)

#     def forward(self, x):
#         x = self.relu(self.layer1(x))
#         feat_layer = self.layer2(x)
#         output = torch.sigmoid(self.layer3(feat_layer))
#         return output.squeeze(), feat_layer

# class SensorModel(nn.Module):
#     def __init__(self, input_dim, hidden_dim=128, output_dim=1, num_layers=2):
#         super(SensorModel, self).__init__()
#         self.lstm = nn.LSTM(input_dim, hidden_dim, num_layers=num_layers, batch_first=True, dropout=0.2)
#         self.fc = nn.Linear(hidden_dim, output_dim)
#         self.sigmoid = nn.Sigmoid()

#     def forward(self, x):
#         # print(x.shape) # (batch_size, input_dim)
#         lstm_out, (ht, ct) = self.lstm(x)
#         penultimate_features = ht[-1]
#         out = self.fc(penultimate_features)
#         out = self.sigmoid(out)  # Apply sigmoid to output
#         # print(out.shape) # why is this 1???
#         return out, penultimate_features  # Output the prediction and penultimate features

class SensorModel(nn.Module):
    def __init__(self, input_dim, hidden_dim=128, output_dim=1, num_layers=2, bidirectional=False, dropout=0.3):
        super(SensorModel, self).__init__()
        
        # Adding bidirectional LSTM
        self.lstm = nn.LSTM(input_dim, hidden_dim, num_layers=num_layers, batch_first=True, 
                             dropout=dropout, bidirectional=bidirectional)
        
        # Output dimension will change based on whether LSTM is bidirectional
        lstm_output_dim = hidden_dim * 2 if bidirectional else hidden_dim
        
        # Adding an extra fully connected layer
        self.fc1 = nn.Linear(lstm_output_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, output_dim)
        
        # Sigmoid activation at the end
        self.sigmoid = nn.Sigmoid()
        
        # Optionally, we could add Batch Normalization to stabilize training
        self.batch_norm = nn.BatchNorm1d(hidden_dim)

    def forward(self, x):
        lstm_out, (ht, ct) = self.lstm(x)
        
        # Use the final hidden state from the last layer of the LSTM
        # For bidirectional LSTM, we concatenate the final forward and backward hidden states
        if self.lstm.bidirectional:
            ht = torch.cat((ht[-2], ht[-1]), dim=1)  # Concatenate the last forward and backward hidden states
        else:
            ht = ht[-1]  # Take the last hidden state if not bidirectional
        
        # Pass through a fully connected layer (fc1)
        fc_out = self.fc1(ht)
        fc_out = self.batch_norm(fc_out)  # Apply batch normalization
        fc_out = torch.relu(fc_out)  # Activation function after batch normalization
        
        # Final output layer (fc2)
        out = self.fc2(fc_out)
        out = self.sigmoid(out)  # Apply sigmoid for binary classification
        
        return out, ht

# function to train sensor model
def train():
    # load and split dataset
    dataset_path = 'datasets/sensor_data.csv'
    dataset = SensorDataset(dataset_path=dataset_path)
    
    features = np.array([item[0].numpy() for item in dataset])
    labels = np.array([item[1].item() for item in dataset])
    train_X, test_X, train_y, test_y = train_test_split(features, labels, test_size=0.1, random_state=42, stratify=labels)

    train_labels = train_y
    test_labels = test_y
    unique, counts = np.unique(train_labels, return_counts=True)
    print(f"Training labels distribution: {dict(zip(unique, counts))}")

    unique, counts = np.unique(test_labels, return_counts=True)
    print(f"Testing labels distribution: {dict(zip(unique, counts))}")

    # class_counts = np.bincount(train_y)
    # neg_weight = class_counts[0]
    # pos_weight = class_counts[1]
    # pos_weight_tensor = torch.tensor([neg_weight / pos_weight], dtype=torch.float32).to(device)

    train_data = TensorDataset(torch.tensor(train_X, dtype=torch.float32), torch.tensor(train_y, dtype=torch.long))
    test_data = TensorDataset(torch.tensor(test_X, dtype=torch.float32), torch.tensor(test_y, dtype=torch.long))
    train_loader = DataLoader(train_data, batch_size=8, shuffle=True)
    test_loader = DataLoader(test_data, batch_size=8, shuffle=False)
    
    input_dim = features.shape[1] 
    print(input_dim)

    # initialize model
    model = SensorModel(input_dim=input_dim).to(device)

    # loss function and optimizer
    # criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight_tensor)
    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.0001)

    # training loop
    num_epochs = 300
    for epoch in range(num_epochs):
        model.train()
        running_loss = 0.0
        correct_predictions = 0
        total_predictions = 0

        for batch_idx, (data, labels) in enumerate(train_loader):
            data, labels = data.to(device), labels.to(device)
            data = data.unsqueeze(1)  # Add sequence dimension (batch_size, 1, input_dim)
            
            optimizer.zero_grad()
            outputs, _ = model(data)
            
            # Ensure outputs have shape [batch_size, 1], labels have shape [batch_size]
            loss = criterion(outputs.squeeze(), labels.float())  # Squeeze to remove extra dimension in outputs
            loss.backward()
            optimizer.step()

            # Predicted values after sigmoid thresholding
            predicted = (outputs > 0.5).long()

            # Increment correct predictions and total predictions
            correct_predictions += (predicted.squeeze() == labels).sum().item()  # Compare predictions with ground truth labels
            total_predictions += labels.size(0)  # Increment by batch size

            running_loss += loss.item()

        # Accuracy calculation after loop over batch
        accuracy = (correct_predictions / total_predictions) * 100
        print(f'Epoch [{epoch+1}/{num_epochs}], Loss: {running_loss/len(train_loader):.4f}, Accuracy: {accuracy:.2f}%')


    # save model
    output_dir = 'results/sensor'
    os.makedirs(output_dir, exist_ok=True)
    model_path = os.path.join(output_dir, 'sensor_model_5.pth')
    torch.save(model.state_dict(), model_path)
    print(f'Model saved to {model_path}')

    model.eval()
    preds, labels_list = [], []

    with torch.no_grad():
        for data, labels in test_loader:
            data, labels = data.to(device), labels.to(device)
            data = data.unsqueeze(1) 
            outputs, _ = model(data)
            
            # Check the shape of outputs to confirm it's of the expected size
            print(f"Outputs shape: {outputs.shape}")  # Debugging line to check shape
            
            # Squeeze to remove extra dimensions (if necessary)
            # Apply sigmoid thresholding to get binary predictions
            predicted = (outputs.squeeze() > 0.5).long()  # Binary prediction (0 or 1)

            # Ensure predicted is a tensor and extend the list with the batch values
            preds.extend(predicted.cpu().numpy().tolist())  # Convert tensor to list
            labels_list.extend(labels.cpu().numpy().tolist())  # Convert tensor to list

    # Convert predictions and labels to lists of integers (if they are not already)
    preds = [int(p) for p in preds]
    labels = [int(l) for l in labels_list]

    # Check lengths of preds and labels
    print(f"Length of preds: {len(preds)}")  # Debugging line
    print(f"Length of labels_list: {len(labels_list)}")  # Debugging line


    with open(os.path.join(output_dir, 'results_5.txt'), 'w') as f:
        f.write("Sensor Model Evaluation Results:\n\n\n")

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
        
        print(f'Results saved to {output_dir}/results_5.txt')
        

if __name__ == '__main__':
    train()
