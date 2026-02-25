import pandas as pd
import numpy as np
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

def train_baseline_model():
    input_file = 'data/cuad_with_risk.csv'
    model_dir = 'models'
    
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found. Please run src/map_risk_labels.py first.")
        return

    print(f"Loading data from {input_file}...")
    df = pd.read_csv(input_file)
    
    # Ensure no missing values in text or label
    df = df.dropna(subset=['clause_text', 'risk_label'])
    
    X = df['clause_text']
    y = df['risk_label']
    
    print("Splitting data (80/20 train/test)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print("Vectorizing text using TF-IDF...")
    tfidf = TfidfVectorizer(max_features=5000, stop_words='english', ngram_range=(1, 2))
    X_train_tfidf = tfidf.fit_transform(X_train)
    X_test_tfidf = tfidf.transform(X_test)
    
    print("Training Logistic Regression classifier...")
    # Using class_weight='balanced' to handle potential class imbalance (e.g. Data Privacy Risk)
    model = LogisticRegression(max_iter=1000, class_weight='balanced', random_state=42)
    model.fit(X_train_tfidf, y_train)
    
    print("Evaluating model...")
    y_pred = model.predict(X_test_tfidf)
    
    acc = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)
    
    print(f"\nAccuracy: {acc:.4f}")
    print("\n--- Classification Report ---")
    print(report)
    
    print("\n--- Confusion Matrix ---")
    print(cm)
    
    # Save model and vectorizer
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)
        
    joblib.dump(model, os.path.join(model_dir, 'baseline.pkl'))
    joblib.dump(tfidf, os.path.join(model_dir, 'tfidf_vectorizer.joblib'))
    print(f"\nModel and vectorizer saved to {model_dir}/")

if __name__ == "__main__":
    train_baseline_model()
