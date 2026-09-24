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