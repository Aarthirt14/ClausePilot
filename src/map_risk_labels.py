import pandas as pd
import os

def map_cuad_to_risk(category):
    """
    Maps 41 CUAD categories into 5 high-level risk labels.
    """
    category_lower = category.lower()
    
    # Define mapping keywords for each group
    risk_mapping = {
        'Termination Risk': [
            'termination', 'renewal', 'extension', 'post-termination', 
            'change control'
        ],
        'Payment Risk': [
            'revenue', 'profit sharing', 'price increases', 'minimum commitment', 
            'volume restriction', 'audit rights'
        ],
        'Liability Risk': [
            'liability', 'indemnification', 'insurance', 'warranty', 
            'non-compete', 'solicitation', 'no-poach', 'assignment',
            'covenant', 'cap on', 'exclusivity', 'most-favored nation'
        ],
        'Data Privacy Risk': [
            'non-disclosure', 'confidentiality', 'data privacy'
        ]
    }
    
    for label, keywords in risk_mapping.items():
        if any(keyword in category_lower for keyword in keywords):
            return label
            
    return 'Neutral'

def main():
    input_file = 'data/cuad_processed.csv'
    output_file = 'data/cuad_with_risk.csv'
    
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found. Please run src/load_data.py first.")
        return

    print(f"Loading data from {input_file}...")
    df = pd.read_csv(input_file)
    
    print("Mapping categories to risk labels...")
    df['risk_label'] = df['original_category'].apply(map_cuad_to_risk)
    
    # Save the updated dataframe
    df.to_csv(output_file, index=False)
    print(f"Updated dataset saved to {output_file}.")
    
    print("\n--- Updated Class Distribution ---")
    distribution = df['risk_label'].value_counts()
    print(distribution)
    
    print("\n--- Examples of Mapping ---")
    sample = df[['original_category', 'risk_label']].drop_duplicates().sample(10)
    print(sample)

if __name__ == "__main__":
    main()
