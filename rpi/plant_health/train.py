import os
import torch
import torch.optim as optim
from torch import nn
from torch.optim import lr_scheduler
from helper.utils import AverageMeter
from tqdm import tqdm

# train function
def train_model(model, device, output_dir, train_loader, val_loader=None, epochs=100, lr=0.001):
    # define criterion, optimizer, and scheduler
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)
    scheduler = lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs, eta_min=1e-6)

    model.to(device)

    best_weights = model.state_dict()
    best_accuracy = 0
    train_loss = AverageMeter()
    val_loss = AverageMeter()
    for epoch in tqdm(range(epochs)):
        # train phase
        model.train()
        correct_preds = 0
        total_preds = 0
        train_loss.reset()
        pbar = tqdm(iterable=train_loader)
        for inputs, labels in pbar:
            inputs = inputs.to(device)
            labels = labels.to(device)

            optimizer.zero_grad()

            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            train_loss.update(loss.item())

            _, preds = torch.max(outputs, 1)
            correct_preds += torch.sum(preds == labels.data)
            total_preds += labels.size(0)

            train_accuracy = float(correct_preds) / float(total_preds)

            pbar.set_description_str('Train Epoch #{}'.format(epoch))
            pbar.set_postfix(train_loss=train_loss.avg, train_acc=train_accuracy)
        pbar.close()

        train_accuracy = correct_preds.double() / total_preds

        # save best model
        if (val_loader is None):
            if train_accuracy > best_accuracy:
                best_accuracy = train_accuracy
                best_weights = model.state_dict()
        else:
            # validation phase
            model.eval()
            val_loss.reset()
            correct_preds = 0
            total_preds = 0
            pbar = tqdm(iterable=val_loader)
            with torch.no_grad():
                for inputs, labels in pbar:
                    inputs = inputs.to(device)
                    labels = labels.to(device)

                    outputs = model(inputs)
                    loss = criterion(outputs, labels)

                    val_loss.update(loss.item())

                    _, preds = torch.max(outputs, 1)
                    correct_preds += torch.sum(preds == labels.data)
                    total_preds += labels.size(0)
                    
                    val_accuracy = float(correct_preds) / float(total_preds)

                    pbar.set_description_str('Val Epoch #{}'.format(epoch))
                    pbar.set_postfix(val_loss=val_loss.avg, val_acc=val_accuracy)
            pbar.close()

            val_accuracy = correct_preds.double() / total_preds

            # save best model
            if val_accuracy > best_accuracy:
                best_accuracy = val_accuracy
                best_weights = model.state_dict()
        
        scheduler.step()

    os.makedirs(output_dir, exist_ok=True)
    # save latest model
    torch.save(model.state_dict(), os.path.join(output_dir, 'last.pth'))
    # save best model
    torch.save(best_weights, os.path.join(output_dir, 'best.pth'))

    # load best model
    model.load_state_dict(best_weights)
    return model