from typing import List, Tuple

import pandas as pd
from sklearn.model_selection import train_test_split


def load_and_split_data(
    data_path: str = "data/cuad_with_risk.csv",
    test_size: float = 0.2,
    seed: int = 42,
) -> Tuple[List[str], List[str], List[str], List[str]]:
    """Load CUAD data and return train/validation splits."""
    df = pd.read_csv(data_path).dropna(subset=["clause_text", "risk_label"])
    x_train, x_val, y_train, y_val = train_test_split(
        df["clause_text"].tolist(),
        df["risk_label"].tolist(),
        test_size=test_size,
        random_state=seed,
        stratify=df["risk_label"],
    )
    return x_train, x_val, y_train, y_val
