# Contract Risk Classification System

A machine learning-powered tool to identify and categorize risks in legal contracts using the CUAD (Contract Understanding Atticus Dataset).

## 🚀 Features
- **Data Pipeline**: Automated fetching and cleaning of the CUAD dataset.
- **Risk Mapping**: Transformation of 41 granular legal categories into 5 high-level risk labels:
  - `Termination Risk`
  - `Liability Risk`
  - `Payment Risk`
  - `Data Privacy Risk`
  - `Neutral`
- **Machine Learning**: TF-IDF + Logistic Regression baseline achieving **~87% accuracy**.
- **PDF Analyzer**: Automated extraction and risk flagging from contract PDFs using `pdfplumber`.

## 📁 Directory Structure
- `data/`: Processed datasets and raw CSVs.
- `models/`: Trained model weights and vectorizers.
- `src/`: Source code for loading, training, and inference.
- `notebooks/`: Exploratory Data Analysis (EDA).

## 🛠️ Setup & Usage

### 1. Environment Setup
```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Data Preparation
```powershell
python src/load_data.py
python src/map_risk_labels.py
```

### 3. Model Training
```powershell
python src/train_baseline.py
```

### 4. Run Analysis
To identify risks in a specific contract PDF:
```powershell
python src/pdf_analyzer.py path/to/contract.pdf
```

## 📊 Performance
The current baseline uses a Logistic Regression model with balanced class weights to handle the inherent imbalance in legal clauses.
- **Accuracy**: 86.87%
- **F1-Score**: 0.87 (Weighted)
