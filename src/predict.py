import joblib
import os
import argparse

def load_model_assets(model_dir='models'):
    model_path = os.path.join(model_dir, 'baseline_logistic_regression.joblib')
    tfidf_path = os.path.join(model_dir, 'tfidf_vectorizer.joblib')
    
    if not os.path.exists(model_path) or not os.path.exists(tfidf_path):
        raise FileNotFoundError("Model or Vectorizer not found. Please run training first.")
        
    model = joblib.load(model_path)
    tfidf = joblib.load(tfidf_path)
    return model, tfidf

def predict_risk(text, model, tfidf):
    """
    Predicts the risk label and confidence for a given clause text.
    """
    if not text.strip():
        return "Neutral", 0.0
        
    X_tfidf = tfidf.transform([text])
    prediction = model.predict(X_tfidf)[0]
    
    # Get probability/confidence
    probabilities = model.predict_proba(X_tfidf)[0]
    class_idx = list(model.classes_).index(prediction)
    confidence = probabilities[class_idx]
    
    return prediction, confidence

def main():
    parser = argparse.ArgumentParser(description="Predict risk label for a clause text.")
    parser.add_argument("text", type=str, help="The clause text to analyze.")
    args = parser.parse_args()
    
    try:
        model, tfidf = load_model_assets()
        label, conf = predict_risk(args.text, model, tfidf)
        
        print(f"\nText: {args.text[:100]}...")
        print(f"Predicted Risk: {label}")
        print(f"Confidence: {conf:.4f}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
