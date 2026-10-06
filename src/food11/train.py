import argparse
from pathlib import Path
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import datasets, models, transforms
import mlflow
import mlflow.pytorch


def parse_args():
    parser = argparse.ArgumentParser(description="Food-11 ResNet18 Training")
    parser.add_argument(
        "--dataset",
        type=str,
        default="mini",
        choices=["mini", "processed"],
        help="Dataset variant to use ('mini' or 'processed')",
    )
    parser.add_argument("--epochs", type=int, default=5, help="Number of epochs")
    parser.add_argument("--lr", type=float, default=0.001, help="Learning rate")
    parser.add_argument("--batch-size", type=int, default=32, help="Batch size")
    return parser.parse_args()


def get_data_loaders(dataset_type, batch_size):
    base_folder = (
        "food11_processed_mini" if dataset_type == "mini" else "food11_processed"
    )
    data_dir = Path("data") / base_folder

    data_transforms = {
        "training": transforms.Compose([
            transforms.RandomHorizontalFlip(),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ]),
        "validation": transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ]),
        "evaluation": transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ]),
    }

    image_datasets = {
        split: datasets.ImageFolder(data_dir / split, transform=data_transforms[split])
        for split in ["training", "validation", "evaluation"]
    }

    loaders = {
        split: DataLoader(
            image_datasets[split],
            batch_size=batch_size,
            shuffle=(split == "training"),
            num_workers=0,
        )
        for split in ["training", "validation", "evaluation"]
    }

    dataset_sizes = {split: len(image_datasets[split]) for split in image_datasets}
    return loaders, dataset_sizes


def train_model(args):
    mlflow.set_tracking_uri("http://127.0.0.1:5000")
    mlflow.set_experiment("food11")

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    loaders, dataset_sizes = get_data_loaders(args.dataset, args.batch_size)

    with mlflow.start_run():
        mlflow.log_params({
            "dataset": args.dataset,
            "epochs": args.epochs,
            "lr": args.lr,
            "batch_size": args.batch_size,
            "architecture": "resnet18",
            "device": str(device),
        })

        model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
        num_ftrs = model.fc.in_features
        model.fc = nn.Linear(num_ftrs, 11)
        model = model.to(device)

        criterion = nn.CrossEntropyLoss()
        optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)

        for epoch in range(args.epochs):
            model.train()
            running_loss = 0.0
            for inputs, labels in loaders["training"]:
                inputs, labels = inputs.to(device), labels.to(device)
                optimizer.zero_grad()
                outputs = model(inputs)
                loss = criterion(outputs, labels)
                loss.backward()
                optimizer.step()
                running_loss += loss.item() * inputs.size(0)

            train_loss = running_loss / dataset_sizes["training"]

            model.eval()
            val_loss = 0.0
            val_corrects = 0
            with torch.no_grad():
                for inputs, labels in loaders["validation"]:
                    inputs, labels = inputs.to(device), labels.to(device)
                    outputs = model(inputs)
                    loss = criterion(outputs, labels)
                    _, preds = torch.max(outputs, 1)
                    val_loss += loss.item() * inputs.size(0)
                    val_corrects += torch.sum(preds == labels.data)

            epoch_val_loss = val_loss / dataset_sizes["validation"]
            epoch_val_acc = (val_corrects.double() / dataset_sizes["validation"]).item()

            print(
                f"Epoch {epoch+1}/{args.epochs} - "
                f"Train Loss: {train_loss:.4f} - "
                f"Val Loss: {epoch_val_loss:.4f} - "
                f"Val Acc: {epoch_val_acc:.4f}"
            )

            mlflow.log_metric("train_loss", train_loss, step=epoch)
            mlflow.log_metric("val_loss", epoch_val_loss, step=epoch)
            mlflow.log_metric("val_accuracy", epoch_val_acc, step=epoch)

        model.eval()
        eval_corrects = 0
        with torch.no_grad():
            for inputs, labels in loaders["evaluation"]:
                inputs, labels = inputs.to(device), labels.to(device)
                outputs = model(inputs)
                _, preds = torch.max(outputs, 1)
                eval_corrects += torch.sum(preds == labels.data)

        test_accuracy = (eval_corrects.double() / dataset_sizes["evaluation"]).item()
        print(f"Test Accuracy: {test_accuracy:.4f}")
        mlflow.log_metric("test_accuracy", test_accuracy)

        # Pass serialization_format="pickle" to use standard PyTorch weights saving:
    mlflow.pytorch.log_model(
    pytorch_model=model,
    artifact_path="model",
    serialization_format="pickle",
)


if __name__ == "__main__":
    args = parse_args()
    train_model(args)