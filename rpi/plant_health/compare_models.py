import os
import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import models, transforms
from dataset import ImageDataset, split_dataset
from train import train_model
from evaluate import evaluate_model
import argparse
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f'torch.cuda.is_available(): {torch.cuda.is_available()}')
print(f'device: {device}')

# load pretrained models
def load_model(model_name='resnet18'):
    if model_name == 'resnet18':
        model = models.resnet18(pretrained=True)
    elif model_name == 'resnet50':
        model = models.resnet50(pretrained=True)
    elif model_name == 'mobilenet_v2':
        model = models.mobilenet_v2(pretrained=True)
    
    # modify the last layer for binary classification
    num_features = model.fc.in_features if 'resnet' in model_name else model.classifier[1].in_features
    if 'resnet' in model_name:
        model.fc = nn.Linear(num_features, 2)
    else:
        model.classifier[1] = nn.Linear(num_features, 2)

    return model

# function to train and compare models
def compare_models():
    parser = argparse.ArgumentParser(description='Compare models for plant health classification.')
    parser.add_argument('--val', action='store_true', help='Use validation set while training')
    parser.add_argument('--dataset', type=str, default='dataset', help='Dataset')
    parser.add_argument('--output', type=str, default='results/compare_models', help='Output directory')
    parser.add_argument('--epochs', type=int, default=100, help='Number of epochs')
    parser.add_argument('--lr', type=float, default=0.001, help='Learning rate')
    parser.add_argument('--grey', action='store_true', help='Use greyscale images')

    args = parser.parse_args()  

    # resize to 224x224 - expected input size for models, ImageNet normalization
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    # load and split dataset
    dataset_path = os.path.join('datasets', args.dataset + '.pkl')
    dataset = ImageDataset(dataset_path=dataset_path, transform=transform, greyscale=args.grey)
    train_dataset, val_dataset, test_dataset = split_dataset(dataset, args.val, val_size=0.15, test_size=0.1, random_seed=42)

    # set dataloaders
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)
    val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False) if (args.val) else None

    # initialize models
    models = [('ResNet18', load_model('resnet18')), 
              ('ResNet50', load_model('resnet50')), 
              ('MobileNetV2', load_model('mobilenet_v2'))]
    trained_models = []

    # train models
    for model_name, model in models:
        print(f'Training {model_name}...')
        output_dir = os.path.join(args.output, args.dataset, model_name)
        print(output_dir)
        trained_models.append((model_name, train_model(model, device, output_dir, train_loader, val_loader, epochs=args.epochs, lr=args.lr)))

    # load already trained models
    for model_name, model in models:
        print(f'Loading {model_name}...')
        model_path = os.path.join(args.output, args.dataset, model_name, 'best.pth')
        if os.path.exists(model_path):
            model.load_state_dict(torch.load(model_path, map_location=device))
            model.to(device)
            model.eval()
            trained_models.append((model_name, model))
        else:
            print(f'Warning: Model file {model_path} not found. Skipping {model_name}.')

    # evaluate models
    with open(os.path.join(args.output, args.dataset, 'comparison_results_2.txt'), 'w') as f:
        f.write(f"Comparison of Models:\n\n")
        f.write(f"Dataset: {args.dataset}\n")
        for model_name, trained_model in trained_models:
            print(f'Evaluating {model_name}...')
            labels, preds = evaluate_model(trained_model, device, test_loader)
            classification_rep = classification_report(labels, preds)

            # format confusion matrix with labels
            conf_matrix = confusion_matrix(labels, preds)
            conf_matrix_df = pd.DataFrame(conf_matrix, 
                                        index=["Actual Healthy", "Actual Unhealthy"], 
                                        columns=["Predicted Healthy", "Predicted Unhealthy"])

            # calculate metrics
            tn, fp, fn, tp = conf_matrix.ravel()
            tpr = tp / (tp + fn)
            tnr = tn / (tn + fp)
            fpr = fp / (fp + tn)
            fnr = fn / (fn + tp)

            f.write(f"{model_name} Evaluation Results:\n{classification_rep}\n")
            f.write(f"Confusion Matrix:\n{conf_matrix_df.to_string()}\n\n")
            f.write(f"True Positive Rate (TPR): {tpr:.4f}\n")
            f.write(f"True Negative Rate (TNR): {tnr:.4f}\n")
            f.write(f"False Positive Rate (FPR): {fpr:.4f}\n")
            f.write(f"False Negative Rate (FNR): {fnr:.4f}\n\n")

            print(classification_rep)
            print(f"Confusion Matrix for {model_name}:\n{conf_matrix_df}")
            print(f"True Positive Rate (TPR): {tpr:.4f}")
            print(f"True Negative Rate (TNR): {tnr:.4f}")
            print(f"False Positive Rate (FPR): {fpr:.4f}")
            print(f"False Negative Rate (FNR): {fnr:.4f}\n")

if __name__ == '__main__':
    compare_models()
