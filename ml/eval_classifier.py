# Evaluates the trained DistilBERT model on test_data.csv (sentences that were NOT used for training).
import sys, types, csv, importlib.abc, importlib.machinery


class _Stub(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    def find_spec(self, fullname, path, target=None):
        if fullname.split(".")[0] in ("scipy", "sklearn"):
            spec = importlib.machinery.ModuleSpec(fullname, self)
            spec.submodule_search_locations = []
            return spec
        return None

    def create_module(self, spec):
        m = types.ModuleType(spec.name)
        m.__path__ = []
        return m

    def exec_module(self, module):
        module.__getattr__ = lambda name: (lambda *a, **k: None)


sys.meta_path.insert(0, _Stub())

import torch
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification

tok = DistilBertTokenizerFast.from_pretrained("./model_store")
model = DistilBertForSequenceClassification.from_pretrained("./model_store")
model.eval()

rows = list(csv.DictReader(open("test_data.csv", encoding="utf-8")))
labels = sorted({r["label"] for r in rows})
conf = {a: {b: 0 for b in labels} for a in labels}
correct = 0
for r in rows:
    enc = tok(r["text"], return_tensors="pt", truncation=True, max_length=64)
    with torch.no_grad():
        pred = model.config.id2label[int(torch.argmax(model(**enc).logits, dim=1))]
    conf[r["label"]][pred] = conf[r["label"]].get(pred, 0) + 1
    correct += pred == r["label"]

lines = [f"Test sentences: {len(rows)}", f"Accuracy: {correct}/{len(rows)} = {100 * correct / len(rows):.1f}%", "",
         f"{'class':20s} {'precision':>9s} {'recall':>8s} {'f1':>6s}"]
for c in labels:
    tp = conf[c][c]
    fp = sum(conf[o].get(c, 0) for o in labels if o != c)
    fn = sum(conf[c].get(o, 0) for o in labels if o != c)
    p = tp / (tp + fp) if tp + fp else 0
    r_ = tp / (tp + fn) if tp + fn else 0
    f1 = 2 * p * r_ / (p + r_) if p + r_ else 0
    lines.append(f"{c:20s} {p:9.2f} {r_:8.2f} {f1:6.2f}")
text = "\n".join(lines)
print(text)
open("eval_results.txt", "w", encoding="utf-8").write(text)
