import pandas as pd
import numpy as np
import os
import torch
import argparse
from torch import nn
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, accuracy_score, classification_report
from transformers import (
    AutoTokenizer, 
    AutoModelForSequenceClassification, 
    Trainer, 
    TrainingArguments, 
    DataCollatorWithPadding
)
from sklearn.utils.class_weight import compute_class_weight

# Set seed for reproducibility
torch.manual_seed(42)

class ClauseDataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)

class WeightedTrainer(Trainer):
    def __init__(self, class_weights, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.class_weights = torch.tensor(class_weights).to(self.args.device)

    def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
        labels = inputs.get("labels")
        outputs = model(**inputs)
        logits = outputs.get("logits")
        loss_fct = nn.CrossEntropyLoss(weight=self.class_weights)
        loss = loss_fct(logits.view(-1, self.model.config.num_labels), labels.view(-1))
        return (loss, outputs) if return_outputs else loss

def compute_metrics(pred):
    labels = pred.label_ids
    preds = pred.predictions.argmax(-1)
    f1 = f1_score(labels, preds, average='weighted')
    acc = accuracy_score(labels, preds)
    return {
        'accuracy': acc,
        'f1': f1,
    }

def train_transformer_model(base_model_name: str, model_output_dir: str):
    input_file = 'data/cuad_with_risk.csv'
    
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return

    print(f"Loading data from {input_file}...")
    df = pd.read_csv(input_file).dropna(subset=['clause_text', 'risk_label'])
    
    # Subsetting for CPU training speed
    if not torch.cuda.is_available() and len(df) > 400:
        print("CPU detected. Subsampling up to 80 records per class for efficient training (~10 min)...")
        samples = []
        for label in df['risk_label'].unique():
            subset = df[df['risk_label'] == label]
            samples.append(subset.sample(min(len(subset), 80), random_state=42))
        df = pd.concat(samples).reset_index(drop=True)
    
    # Label Encoding
    unique_labels = sorted(df['risk_label'].unique())
    label2id = {label: i for i, label in enumerate(unique_labels)}
    id2label = {i: label for label, i in label2id.items()}
    df['label'] = df['risk_label'].map(label2id)
    
    # Class Weights
    class_weights = compute_class_weight(
        class_weight='balanced',
        classes=np.unique(df['label']),
        y=df['label']
    ).astype(np.float32)
    
    # Split
    train_texts, val_texts, train_labels, val_labels = train_test_split(
        df['clause_text'].tolist(), 
        df['label'].tolist(), 
        test_size=0.2, 
        random_state=42, 
        stratify=df['label']
    )
    
    print(f"Initializing Tokenizer ({base_model_name})...")
    tokenizer = AutoTokenizer.from_pretrained(base_model_name)
    
    max_len = 128 if not torch.cuda.is_available() else 512
    print(f"Tokenizing (max_length={max_len})...")
    train_encodings = tokenizer(train_texts, truncation=True, padding=True, max_length=max_len)
    val_encodings = tokenizer(val_texts, truncation=True, padding=True, max_length=max_len)
    
    train_dataset = ClauseDataset(train_encodings, train_labels)
    val_dataset = ClauseDataset(val_encodings, val_labels)
    
    print("Loading Model...")
    model = AutoModelForSequenceClassification.from_pretrained(
        base_model_name, 
        num_labels=len(unique_labels),
        id2label=id2label,
        label2id=label2id
    )
    
    # Determine batch size based on GPU availability
    device = "cuda" if torch.cuda.is_available() else "cpu"
    batch_size = 8 if device == "cuda" else 4
    print(f"Using device: {device}, Batch size: {batch_size}")
    
    num_epochs = 2 if not torch.cuda.is_available() else 3
    training_args = TrainingArguments(
        output_dir='./results',
        num_train_epochs=num_epochs,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        warmup_steps=100,
        weight_decay=0.01,
        logging_dir='./logs',
        logging_steps=50,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        fp16=torch.cuda.is_available(),
        report_to="none"
    )
    
    trainer = WeightedTrainer(
        class_weights=class_weights,
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        processing_class=tokenizer,
        compute_metrics=compute_metrics,
    )
    
    print("Starting Training...")
    trainer.train()
    
    print("Evaluating...")
    eval_results = trainer.evaluate()
    print(f"\nFinal Evaluation Results: {eval_results}")
    
    # Final classification report
    preds = trainer.predict(val_dataset)
    y_pred = preds.predictions.argmax(-1)
    print("\n--- BERT Classification Report ---")
    print(classification_report(val_labels, y_pred, target_names=unique_labels))
    
    print(f"Saving model to {model_output_dir}...")
    os.makedirs(model_output_dir, exist_ok=True)
    trainer.save_model(model_output_dir)
    tokenizer.save_pretrained(model_output_dir)
    print("Model saved successfully.")


def train_bert_and_legal_bert(train_both: bool = True):
    train_transformer_model(
        base_model_name="bert-base-uncased",
        model_output_dir="models/bert_model",
    )

    if train_both:
        train_transformer_model(
            base_model_name="nlpaueb/legal-bert-base-uncased",
            model_output_dir="models/legal_bert_model",
        )


def parse_args():
    parser = argparse.ArgumentParser(description="Train BERT-based contract risk classifiers.")
    parser.add_argument(
        "--model",
        choices=["bert", "legal-bert", "both"],
        default="both",
        help="Select which model(s) to train.",
    )
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    if args.model == "bert":
        train_transformer_model("bert-base-uncased", "models/bert_model")
    elif args.model == "legal-bert":
        train_transformer_model("nlpaueb/legal-bert-base-uncased", "models/legal_bert_model")
    else:
        train_bert_and_legal_bert(train_both=True)
