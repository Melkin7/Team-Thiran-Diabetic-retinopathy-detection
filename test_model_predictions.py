#!/usr/bin/env python3
"""
Diagnostic script to check model predictions
"""
import torch
import numpy as np
from model import model, test_transforms, classes
from PIL import Image
import sys

print("Model Diagnostic Test")
print("=" * 50)

# Check if model is in eval mode
print(f"Model training mode: {model.training}")
print(f"Device: {next(model.parameters()).device}")

# Create a dummy test image to see raw outputs
dummy_img = torch.randn(1, 3, 224, 224)  # Random image
model.eval()
with torch.no_grad():
    out = model(dummy_img)
    ps = torch.exp(out)
    print(f"\nRaw model output (logits): {out}")
    print(f"Probabilities (softmax): {ps}")
    print(f"Predicted class: {ps.argmax().item()}")

# Test with a sample image if path provided
if len(sys.argv) > 1:
    img_path = sys.argv[1]
    print(f"\nTesting with image: {img_path}")
    img = Image.open(img_path).convert('RGB')
    img_tensor = test_transforms(img).unsqueeze(0)
    
    with torch.no_grad():
        out = model(img_tensor)
        ps = torch.exp(out)
        print(f"Raw output: {out}")
        print(f"Probabilities: {ps}")
        print(f"Predicted: {classes[ps.argmax().item()]}")

print("\n" + "=" * 50)
print("Check if all probabilities are similar - that indicates untrained model")
