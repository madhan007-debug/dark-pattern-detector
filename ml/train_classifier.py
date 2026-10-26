import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from transformers import (
    DistilBertTokenizerFast,
    DistilBertForSequenceClassification,
    Trainer,
    TrainingArguments,
)
import torch
from torch.utils.data import Dataset

# ---- Step 1: Load and prepare data ----
df = pd.read_csv("training_data.csv")

labels = sorted(df["label"].unique().tolist())
label2id = {label: i for i, label in enumerate(labels)}
id2label = {i: label for i, label in enumerate(labels)}
df["label_id"] = df["label"].map(label2id)

print(f"Categories found: {labels}")
print(f"Total examples: {len(df)}")

train_texts, val_texts, train_labels, val_labels = train_test_split(
    df["text"].tolist(), df["label_id"].tolist(), test_size=0.15, random_state=42, stratify=df["label_id"]
)

# ---- Step 2: Tokenize ----
tokenizer = DistilBertTokenizerFast.from_pretrained("distilbert-base-uncased")

train_encodings = tokenizer(train_texts, truncation=True, padding=True, max_length=64)
val_encodings = tokenizer(val_texts, truncation=True, padding=True, max_length=64)


class DarkPatternDataset(Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item["labels"] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)


train_dataset = DarkPatternDataset(train_encodings, train_labels)
val_dataset = DarkPatternDataset(val_encodings, val_labels)

# ---- Step 3: Load model ----
model = DistilBertForSequenceClassification.from_pretrained(
    "distilbert-base-uncased",
    num_labels=len(labels),
    id2label=id2label,
    label2id=label2id,
)

# ---- Step 4: Train ----
training_args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=25,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    eval_strategy="epoch",
    save_strategy="no",
    logging_steps=5,
    learning_rate=5e-5,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
)

print("Starting training...")
trainer.train()

# ---- Step 5: Save the model ----
model.save_pretrained("./model_store")
tokenizer.save_pretrained("./model_store")
print("Model saved to ./model_store")