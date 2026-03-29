import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from segmentation.segmenter import ContractSegmenter
from classification.risk_scorer import RiskScorer

def test_system():
    # 1. Test Segmentation
    segmenter = ContractSegmenter()
    base_dir = os.path.dirname(os.path.abspath(__file__))
    sample_path = os.path.join(base_dir, 'sample_contract.txt')
    
    if os.path.exists(sample_path):
        text = segmenter.extract_text(sample_path)
    else:
        text = "1. Termination\nEither party can terminate.\n2. Liability\nUncapped damages."
    
    clauses = segmenter.segment_into_clauses(text)
    print(f"Total clauses found: {len(clauses)}")
    for i, c in enumerate(clauses[:2]):
        print(f"Clause {i+1}: {c[:50]}...")

    # 2. Test Scoring 
    scorer = RiskScorer()
    high_risk_found = None
    for clause in clauses[:3]:
        result = scorer.score_clause(clause)
        print(f"Clause: {clause[:30]}... | Risk: {result['risk_level']} | Confidence: {result['confidence']:.2%}")
        if result['risk_level'] in ['High', 'Medium'] and not high_risk_found:
            high_risk_found = (clause, result['risk_level'])

    # 3. Test Explanation
    from explanation.explainer import RiskExplainer
    if os.getenv("GOOGLE_API_KEY"):
        explainer = RiskExplainer()
        test_clause, risk = high_risk_found if high_risk_found else ("Uncapped Liability.", "High")
        explanation = explainer.generate_explanation(test_clause, risk)
        print(f"\\nTest Explanation for '{risk}':\\n{explanation[:100]}...")
    else:
        print("\\nSkipping explanation test (no API key).")

if __name__ == "__main__":
    test_system()
