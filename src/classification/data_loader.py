import os
import pandas as pd
from datasets import load_dataset
import torch

class CUADDataLoader:
    def __init__(self, dataset_name="theatticusproject/cuad-qa"):
        self.dataset_name = dataset_name
        self.risk_mapping = {
            # High Risk (2) - Critical clauses that impact liability and competition
            'Cap on Liability': 2,
            'Uncapped Liability': 2,
            'Indemnification': 2,
            'IP Ownership Assignment': 2,
            'Change of Control': 2,
            'Exclusivity': 2,
            'Non-Compete': 2,
            'Most Favored Nation': 2,
            'Liquidated Damages': 2,
            'Price Restrictions': 2,
            'Revenue/Profit Sharing': 2,
            'Non-Solicit of Customers': 2,
            'No-Solicit of Employees': 2,
            'No-Hiring': 2,

            # Medium Risk (1) - Operationally significant clauses
            'Termination for Convenience': 1,
            'Termination for Cause': 1,
            'Audit Rights': 1,
            'Confidentiality': 1,
            'License Grant': 1,
            'Insurance': 1,
            'Minimum Commitment': 1,
            'Warranty': 1,
            'Non-Disparagement': 1,
            'Anti-Assignment': 1,
            'Competitive Restriction Exception': 1,
            'Rofr/Rofo/Rofn': 1,
            'Post-Termination Services': 1,

            # Low Risk (0) - Standard boilerplates and general info
            'Governing Law': 0,
            'Effective Date': 0,
            'Expiration Date': 0,
            'Renewal Term': 0,
            'Notice Period to Terminate Renewal': 0,
            'Document Name': 0,
            'Parties': 0,
            'Agreement Date': 0,
            'Covenant Not to Sue': 0,
            'Third Party Beneficiary': 0,
            'Force Majeure': 0,
            'Affiliate License-Licensor': 0,
            'Affiliate License-Licensee': 0,
            'Joint IP Ownership': 0,
            'Non-Transferable License': 0,
            'Unlimited/Irrevocable License': 0,
            'Volume Restriction': 0
        }

    def get_risk_level(self, question):
        """Maps a question string to a risk level (0, 1, 2) using keywords."""
        for key, value in self.risk_mapping.items():
            if key.lower() in question.lower():
                return value
        return 0 # Default to Low

    def load_and_preprocess(self):
        """Loads CUAD dataset and prepares it for clause-level classification."""
        print(f"Loading dataset: {self.dataset_name}...")
        # Note: trust_remote_code=True may be required depending on datasets version
        try:
            dataset = load_dataset(self.dataset_name, trust_remote_code=True)
        except TypeError:
            dataset = load_dataset(self.dataset_name)
        
        processed_data = []
        
        for split in ['train', 'test']:
            if split not in dataset: continue
            for item in dataset[split]:
                # Flattened CUAD-QA: Each item has 'question' and 'answers'
                question = item['question']
                risk_level = self.get_risk_level(question)
                
                # 'answers' is a dict with 'text' (list)
                for clause_text in item['answers']['text']:
                    processed_data.append({
                        'text': clause_text,
                        'label': risk_level
                    })

        df = pd.DataFrame(processed_data)
        return df

if __name__ == "__main__":
    loader = CUADDataLoader()
    # This might take time and disk space, so we won't run it here automatically.
    # df = loader.load_and_preprocess()
    # print(df.head())
    pass
