import sys
import os

# Try to load the model and report any issues
try:
    from model import model
    print("✅ SUCCESS: Model loaded successfully!")
    print(f"Model type: {type(model)}")
except Exception as e:
    print(f"❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
