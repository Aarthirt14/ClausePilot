import pandas as pd
from datasets import load_dataset

import requests
import os

def download_cuad_json(url, target_path):
    if os.path.exists(target_path):
        print(f"File already exists at {target_path}")
        return
    
    print(f"Downloading CUAD JSON from {url}...")
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    with open(target_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    print("Download complete.")

def load_cuad_to_df():
    url = "https://huggingface.co/datasets/theatticusproject/cuad/resolve/main/CUAD_v1/CUAD_v1.json"
    target_path = "data/CUAD_v1.json"
    
    if not os.path.exists('data'):
        os.makedirs('data')
        
    download_cuad_json(url, target_path)
    
    print("Loading and parsing JSON...")
    # Using the datasets library to load local json
    dataset = load_dataset("json", data_files=target_path, field="data")
    
    data_rows = []
    
    for doc in dataset['train']:
        title = doc.get('title', 'Unknown')
        for paragraph in doc['paragraphs']:
            context = paragraph['context']
            for qas in paragraph['qas']:
                category = qas['question']
                answers = qas['answers']
                
                if answers:
                    for answer in answers:
                        data_rows.append({
                            'clause_text': answer['text'],
                            'original_category': category,
                            'context': context,
                            'title': title
                        })
    
    df = pd.DataFrame(data_rows)
    return df[['clause_text', 'original_category']].copy()

if __name__ == "__main__":
    df = load_cuad_to_df()
    
    print("\n--- First 5 rows ---")
    print(df.head())
    
    print("\n--- Number of unique categories ---")
    print(df['original_category'].nunique())
    
    print("\n--- Class distribution (Top 10) ---")
    print(df['original_category'].value_counts().head(10))
    
    # Save a sample to data/ for future use
    import os
    if not os.path.exists('data'):
        os.makedirs('data')
    df.to_csv('data/cuad_processed.csv', index=False)
    print(f"\nProcessed data saved to 'data/cuad_processed.csv'. Total rows: {len(df)}")
