import io
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, File, UploadFile
import mlflow.pyfunc
from PIL import Image
import torch
from torchvision import transforms

CLASSES = [
    "Bread",
    "Dairy product",
    "Dessert",
    "Egg",
    "Fried food",
    "Meat",
    "Noodles/Pasta",
    "Rice",
    "Seafood",
    "Soup",
    "Vegetable/Fruit",
]

eval_transforms = transforms.Compose([
    transforms.Resize((128, 128)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
])

model = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global model
    tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000")
    mlflow.set_tracking_uri(tracking_uri)
    model = mlflow.pyfunc.load_model("models:/food11@champion")
    yield


app = FastAPI(title="Food-11 Classifier API", lifespan=lifespan)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    contents = await file.read()
    image = Image.open(io.BytesIO(contents)).convert("RGB")

    tensor = eval_transforms(image).unsqueeze(0)

    preds = model.predict(tensor.numpy())
    torch_preds = torch.tensor(preds)
    probs = torch.softmax(torch_preds, dim=1)

    conf, pred_idx = torch.max(probs, dim=1)
    class_idx = pred_idx.item()

    return {
        "prediction": CLASSES[class_idx],
        "confidence": round(conf.item(), 4),
        "class_index": class_idx,
    }
