from typing import Dict, List, Tuple

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression


def train_baseline(
    texts: List[str],
    labels: List[str],
) -> Tuple[LogisticRegression, TfidfVectorizer]:
    """Train TF-IDF + Logistic Regression baseline."""
    vectorizer = TfidfVectorizer(max_features=5000, stop_words="english", ngram_range=(1, 2))
    x_tfidf = vectorizer.fit_transform(texts)

    model = LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42)
    model.fit(x_tfidf, labels)

    return model, vectorizer


def baseline_predict(
    model: LogisticRegression,
    vectorizer: TfidfVectorizer,
    texts: List[str],
) -> Tuple[List[str], List[float]]:
    """Predict labels and confidence using baseline model."""
    x_tfidf = vectorizer.transform(texts)
    preds = model.predict(x_tfidf)
    probs = model.predict_proba(x_tfidf)

    confidences: List[float] = []
    for row_idx, pred_label in enumerate(preds):
        class_idx = list(model.classes_).index(pred_label)
        confidences.append(float(probs[row_idx][class_idx]))

    return list(preds), confidences


def baseline_predict_proba(
    model: LogisticRegression,
    vectorizer: TfidfVectorizer,
    texts: List[str],
) -> np.ndarray:
    """Return full probability distribution for calibration analysis."""
    x_tfidf = vectorizer.transform(texts)
    return model.predict_proba(x_tfidf)
