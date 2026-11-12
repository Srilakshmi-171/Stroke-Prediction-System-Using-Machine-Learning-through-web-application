"""
Check if all required models exist
"""

import os

required_models = [
    'models/brain_ml.pkl',
    'models/brain_ann.h5',
    'models/brain_cnn.h5',
    'models/heart_ml.pkl',
    'models/heart_ann.h5',
    'models/heart_cnn.h5',
    'models/scaler.pkl',
    'models/encoder.pkl'
]

print("="*60)
print("Checking model files...")
print("="*60)

missing = []
for model in required_models:
    if os.path.exists(model):
        size = os.path.getsize(model) / 1024  # Size in KB
        print(f"✓ {model} ({size:.1f} KB)")
    else:
        print(f"✗ {model} (MISSING)")
        missing.append(model)

print("\n" + "="*60)
if missing:
    print(f"\n⚠️  Missing {len(missing)} model files. Run training script:")
    print("python models/train_updated_models.py")
else:
    print("\n✓ All models present! You can run the application.")
print("="*60)