import torch

# evaluate function
def evaluate_model(model, device, test_loader):
    model.eval()
    all_preds = []
    all_labels = []
    
    model.to(device)
    with torch.no_grad():
        for inputs, labels in test_loader:
            inputs = inputs.to(device)
            labels = labels.to(device)

            outputs = model(inputs)
            _, preds = torch.max(outputs, 1)

            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
    return all_labels, all_preds
