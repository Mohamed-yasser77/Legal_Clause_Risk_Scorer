import os
import torch
import zipfile
from transformers import AutoTokenizer, AutoModelForSequenceClassification

def unzip_model(zip_path, extract_to):
    """Unzips the model if the directory doesn't exist."""
    if not os.path.exists(extract_to):
        print(f"📦 Extracting model from {zip_path}...")
        os.makedirs(os.path.dirname(extract_to), exist_ok=True)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        print("✅ Model extracted successfully.")
    else:
        print(f"ℹ️ Model already exists at {extract_to}.")

def test_model():
    # Paths - Correctly point to the root from the tests/ directory
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(tests_dir) # Go up one level to root
    model_zip = os.path.join(base_dir, "legal_risk_model.zip")
    model_dir = os.path.join(base_dir, "models", "legal_risk_model")
    
    # 1. Ensure model is unzipped
    if os.path.exists(model_zip) and not os.path.exists(model_dir):
        unzip_model(model_zip, model_dir)
    
    # 2. Load Model & Tokenizer
    print(f"🚀 Loading fine-tuned model from {model_dir}...")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_dir)
        model = AutoModelForSequenceClassification.from_pretrained(model_dir).to(device)
        model.eval()
        print("✅ Model loaded successfully.")
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return

    # 3. Test Clauses
    test_clauses = [
        {
            "label": "High Risk (Unrestricted Liability)",
            "text": "The Company shall have no liability whatsoever for any damages, whether direct, indirect, incidental, or consequential, arising out of or in connection with this agreement, even if advised of the possibility of such damages."
        },
        {
            "label": "Medium Risk (Manual Renewal/Ambiguous)",
            "text": "This agreement shall automatically renew for successive one-year terms unless either party provides written notice of non-renewal at least 30 days prior to the end of the current term."
        },
        {
            "label": "Low Risk (Standard Confidentiality)",
            "text": "The parties agree to keep the terms of this agreement confidential and not disclose them to any third party without the prior written consent of the other party."
        }
    ]

    index_to_label = {0: "Low", 1: "Medium", 2: "High"}

    print("\n--- ⚖️ Legal Risk Classification Results ---")
    
    for i, clause in enumerate(test_clauses):
        inputs = tokenizer(clause['text'], return_tensors="pt", truncation=True, padding=True, max_length=512).to(device)
        
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits
            probs = torch.softmax(logits, dim=-1)
            prediction = torch.argmax(logits, dim=-1).item()
            confidence = probs[0][prediction].item()

        predicted_label = index_to_label[prediction]
        
        print(f"\nTest {i+1}: {clause['label']}")
        print(f"Clause: \"{clause['text'][:100]}...\"")
        print(f"Predicted Risk: {predicted_label} (Confidence: {confidence:.2%})")
        
        # Check if match (just for demonstration)
        if predicted_label.lower() in clause['label'].lower():
            print("✨ Match!")
        else:
            print("⚠️ Different from expected label.")

if __name__ == "__main__":
    test_model()
