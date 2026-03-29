import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

class RiskScorer:
    def __init__(self, model_path=None):
        # Corrected path to version 1 of the model
        if model_path is None:
            import os
            model_path = os.path.join(os.path.dirname(__file__), '..', '..', 'models', 'legal_risk_model_v1')
            
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Using device: {self.device}")

        # Expert keyword mapping for hybrid scoring (failsafe)
        self.risk_mapping = {
            'Cap on Liability': 2, 'Uncapped Liability': 2, 'Indemnification': 2, 
            'IP Ownership Assignment': 2, 'Exclusivity': 2, 'Non-Compete': 2,
            'Termination for Convenience': 1, 'Audit Rights': 1, 'Confidentiality': 1,
            'Insurance': 1, 'Warranty': 1, 'Rofr/Rofo/Rofn': 1
        }
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_path).to(self.device)
            self.model.eval()
            self.model_loaded = True
        except Exception as e:
            print(f"Warning: Could not load model from {model_path}. Defaulting to base LegalBERT for demonstration. Error: {e}")
            self.tokenizer = AutoTokenizer.from_pretrained("nlpaueb/legal-bert-base-uncased")
            self.model = AutoModelForSequenceClassification.from_pretrained("nlpaueb/legal-bert-base-uncased", num_labels=3).to(self.device)
            self.model.eval()
            self.model_loaded = False

        self.index_to_label = {0: "Low", 1: "Medium", 2: "High"}

    def score_clause(self, clause_text):
        """Classifies a clause using a hybrid of Transformer and Expert Keywords."""
        # 1. Keyword Check (Expert Rule Override)
        for keyword, risk_idx in self.risk_mapping.items():
            if keyword.lower() in clause_text.lower():
                # We prioritize High Risk keywords if they are explicitly present
                if risk_idx == 2:
                    return {
                        "risk_level": "High",
                        "confidence": 0.95,
                        "method": "Expert Keyword Match"
                    }

        # 2. Transformer Inference
        inputs = self.tokenizer(clause_text, return_tensors="pt", truncation=True, padding=True, max_length=512).to(self.device)
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            probs = torch.softmax(logits, dim=-1)[0]
            prediction = torch.argmax(logits, dim=-1).item()
        
        risk_level = self.index_to_label[prediction]
        confidence = probs[prediction].item()
        
        # 3. Hybrid Logic: If the model is unsure, but we found a medium keyword, boost it.
        if confidence < 0.6:
            for keyword, risk_idx in self.risk_mapping.items():
                if keyword.lower() in clause_text.lower():
                    risk_level = self.index_to_label[risk_idx]
                    confidence = 0.8 # Boosted confidence for expert match
                    method = "Hybrid (Model + Keyword)"
                    break
            else:
                method = "Transformer Inference"
        else:
            method = "Transformer Inference"
        
        return {
            "risk_level": risk_level,
            "confidence": confidence,
            "method": method
        }

if __name__ == "__main__":
    # Example usage
    # scorer = RiskScorer()
    # result = scorer.score_clause("This is a sample legal clause.")
    # print(result)
    pass
