import os
import torch
import numpy as np
import argparse
from dataset import SensorDataset
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, AdaBoostClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f'torch.cuda.is_available(): {torch.cuda.is_available()}')
print(f'device: {device}')

# function to train and compare models
def compare_sensor_models():
    parser = argparse.ArgumentParser(description='Compare sesnsor models for plant health classification.')
    parser.add_argument('--dataset', type=str, default='sensor_data', help='Dataset')
    parser.add_argument('--output', type=str, default='results/compare_sensor_models', help='Output directory')

    args = parser.parse_args()  

    # load and split dataset
    dataset_path = os.path.join('datasets', args.dataset + '.csv')
    dataset = SensorDataset(dataset_path=dataset_path)
    features = np.array([item[0].numpy() for item in dataset])
    labels = np.array([item[1].item() for item in dataset])
    train_X, test_X, train_y, test_y = train_test_split(features, labels, test_size=0.1, random_state=42, stratify=labels)

    # initialize models
    models = {
        "KNN Classifier": KNeighborsClassifier(),
        "Decision Tree": DecisionTreeClassifier(random_state=42),
        "Random Forest": RandomForestClassifier(random_state=42),
        "Gradient Boosting": GradientBoostingClassifier(random_state=42),
        "Logistic Regression": LogisticRegression(random_state=42),
        "SVM": SVC(random_state=42),
        "MLP": MLPClassifier(random_state=42),
        "AdaBoost": AdaBoostClassifier(random_state=42)
    }
    
    output_dir = os.path.join(args.output, args.dataset)
    os.makedirs(output_dir, exist_ok=True)
    
    results = []
    for model_name, model in models.items():
        print(f"Training {model_name}...")
        
        # train
        model.fit(train_X, train_y)
        
        # evaluate
        pred_y = model.predict(test_X)
        results.append((model_name, classification_report(test_y, pred_y)))

        # save trained model in output_dir

    with open(os.path.join(output_dir, 'comparison_results.txt'), 'w') as f:
        f.write(f"Comparison of Models:\n\n")
        f.write(f"Dataset: {args.dataset}\n")
        for model_name, classification_rep in results:
            f.write(f"{model_name} Evaluation Results:\n{classification_rep}\n\n")
            print(classification_rep)

if __name__ == '__main__':
    compare_sensor_models()
