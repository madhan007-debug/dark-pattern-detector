import sys
import types
import importlib.abc
import importlib.machinery


class _BlockedPackageStub(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    """
    Windows Application Control blocks native DLLs inside scipy/scikit-learn.
    We don't need either package for text classification - transformers only
    imports them for unrelated optional features. This intercepts any import
    of these packages and returns a harmless empty stub instead.
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
import re

MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ml", "model_store")

tokenizer = DistilBertTokenizerFast.from_pretrained(MODEL_PATH)
model = DistilBertForSequenceClassification.from_pretrained(MODEL_PATH)
model.eval()


def classify_text(text: str, threshold: float = 0.6) -> dict:
    chunks = [c.strip() for c in re.split(r"[\n.!?]+", text) if 15 <= len(c.strip()) <= 250]
    chunks = chunks[:40]
    if not chunks:
        return {"detected": False, "category": "none", "confidence": 0.0}

    inputs = tokenizer(chunks, return_tensors="pt", truncation=True, padding=True, max_length=64)
    with torch.no_grad():
        outputs = model(**inputs)
    probs = torch.softmax(outputs.logits, dim=1)

    best = {"detected": False, "category": "none", "confidence": 0.0}
    for i in range(len(chunks)):
        pred_id = torch.argmax(probs[i]).item()
        label = model.config.id2label[pred_id]
        conf = probs[i][pred_id].item()
        if label != "none" and conf >= threshold and conf > best["confidence"]:
            best = {"detected": True, "category": label, "confidence": round(conf, 3)}
        print("ML flagged:", chunks[i], "->", label, round(conf, 3))
    return best