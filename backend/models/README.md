# Model artifacts

Runtime expects `resnet50_embedding.onnx` in this directory by default.

Generate it from the backend directory:

```bash
pip install -r requirements-export.txt
python scripts/export_resnet50_onnx.py
```

The `.onnx` file is intentionally ignored by git because it is a large binary artifact.
