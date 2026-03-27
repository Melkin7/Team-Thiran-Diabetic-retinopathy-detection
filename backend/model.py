# Importing all packages
import numpy as np
from torch import nn
from torch import optim
import torchvision
import torch
from torchvision import models
from PIL import Image
from torch.optim import lr_scheduler
import os
import sys

print('Imported packages')

# ── Device ───────────────────────────────────────────────────────────────────
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ── Constants ─────────────────────────────────────────────────────────────────
classes = ['No DR', 'Mild', 'Moderate', 'Severe', 'Proliferative DR']

test_transforms = torchvision.transforms.Compose([
    torchvision.transforms.Resize((224, 224)),
    torchvision.transforms.ToTensor(),
    torchvision.transforms.Normalize(
        mean=(0.485, 0.456, 0.406),
        std=(0.229, 0.224, 0.225)
    )
])

# ── Dynamic path resolution ───────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, '..', 'models', 'classifier.pt')

# ── Model Architecture ────────────────────────────────────────────────────────
def build_model():
    model = models.resnet152(weights=None)
    num_ftrs = model.fc.in_features
    model.fc = nn.Sequential(
        nn.Linear(num_ftrs, 512),
        nn.ReLU(),
        nn.Linear(512, 5),
        nn.LogSoftmax(dim=1)
    )
    model.to(device)

    for name, child in model.named_children():
        if name in ['layer2', 'layer3', 'layer4', 'fc']:
            for param in child.parameters():
                param.requires_grad = True
        else:
            for param in child.parameters():
                param.requires_grad = False

    return model

# ── Load Model ────────────────────────────────────────────────────────────────
def load_model(path=MODEL_PATH):
    """Load model from checkpoint - handles multiple formats"""
    model = build_model()
    optimizer = torch.optim.Adam(
        filter(lambda p: p.requires_grad, model.parameters()), lr=0.000001
    )
    
    try:
        checkpoint = torch.load(path, map_location='cpu', weights_only=False)
        
        # Handle different checkpoint formats
        if isinstance(checkpoint, dict):
            # Old format: checkpoint with 'model_state_dict' key
            if 'model_state_dict' in checkpoint:
                model.load_state_dict(checkpoint['model_state_dict'])
                if 'optimizer_state_dict' in checkpoint:
                    optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
            # New format: direct state dict
            else:
                model.load_state_dict(checkpoint)
        else:
            # State dict directly
            model.load_state_dict(checkpoint)
        
        model.eval()
        print("✅ Model loaded successfully")
        return model
    
    except KeyError as e:
        print(f"❌ KeyError loading model: {e}")
        print("   Trying alternative checkpoint format...")
        try:
            model.load_state_dict(checkpoint)
            model.eval()
            print("✅ Model loaded with alternative format")
            return model
        except Exception as e2:
            print(f"❌ Failed to load model: {e2}")
            raise

# ── Inference ─────────────────────────────────────────────────────────────────
def inference(model, file, transform, classes):
    img = Image.open(file).convert('RGB')
    tensor = transform(img).unsqueeze(0).to(device)
    print('Transforming image...')
    with torch.no_grad():
        print('Running inference...')
        out = model(tensor)
        ps = torch.exp(out)
        top_p, top_class = ps.topk(1, dim=1)
        value = top_class.item()
        confidence = round(top_p.item(), 4)
        print(f"Predicted: {classes[value]} (confidence: {confidence})")
        return value, classes[value], confidence

# ── Main callable (used by FastAPI) ──────────────────────────────────────────
def main(path, model):
    value, label, confidence = inference(model, path, test_transforms, classes)
    return value, label, confidence