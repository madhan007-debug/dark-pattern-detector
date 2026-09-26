import sys
import types
import importlib.abc
import importlib.machinery


class _BlockedPackageStub(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    """
    Windows Application Control blocks native DLLs inside scipy/scikit-learn.
    We don't need either package for text classification - transformers only
    imports them for unrelated optional features (object detection loss,
    generation candidate scoring). This intercepts any import of these
    packages, at any depth, and returns a harmless empty stub instead of
    touching the blocked files.
    """
    STUB_ROOTS = ("scipy", "sklearn")

    def find_spec(self, fullname, path, target=None):
        root = fullname.split(".")[0]
        if root in self.STUB_ROOTS:
            spec = importlib.machinery.ModuleSpec(fullname, self)
            spec.submodule_search_locations = []
            return spec
        return None

    def create_module(self, spec):
        module = types.ModuleType(spec.name)
        module.__path__ = []
        return module

    def exec_module(self, module):
        def _dummy(*args, **kwargs):
            return None
        module.__getattr__ = lambda name: _dummy


sys.meta_path.insert(0, _BlockedPackageStub())

from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification
import torch
import os

MODEL_PATH = os.path.join("..", "ml", "model_store")

tokenizer = DistilBertTokenizerFast.from_pretrained(MODEL_PATH)
model = DistilBertForSequenceClassification.from_pretrained(MODEL_PATH)
model.eval()

def classify_text(text: str) -> dict:
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=64)
    with torch.no_grad():
        outputs = model(**inputs)
    probs = torch.softmax(outputs.logits, dim=1)
    pred_id = torch.argmax(probs, dim=1).item()
    confidence = probs[0][pred_id].item()
    label = model.config.id2label[pred_id]
    if label == "none":
        return {"detected": False, "category": "none", "confidence": round(confidence, 3)}
    return {"detected": True, "category": label, "confidence": round(confidence, 3)}