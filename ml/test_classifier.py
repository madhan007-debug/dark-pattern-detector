from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification
import torch

tokenizer = DistilBertTokenizerFast.from_pretrained("./model_store")
model = DistilBertForSequenceClassification.from_pretrained("./model_store")

def classify(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=64)
    with torch.no_grad():
        outputs = model(**inputs)
    probs = torch.softmax(outputs.logits, dim=1)
    pred_id = torch.argmax(probs, dim=1).item()
    confidence = probs[0][pred_id].item()
    label = model.config.id2label[pred_id]
    return {"category": label, "confidence": round(confidence, 3)}

if __name__ == "__main__":
    test_samples = [
        "Only 2 left in stock, hurry!",
        "Your free trial will auto-renew unless cancelled",
        "Thank you for your order",
        "No thanks, I don't want to save money",
    ]
    for s in test_samples:
        print(s, "->", classify(s))