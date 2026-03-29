import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class RiskExplainer:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key or api_key == "your_api_key_here":
            print("Warning: GOOGLE_API_KEY not found in .env. Explanation generation will fail.")
        else:
            genai.configure(api_key=api_key)
        # Using gemini-1.5-pro or gemini-1.5-flash for general reasoning
        self.model = genai.GenerativeModel('gemini-1.5-pro')

    def generate_explanation(self, clause_text, risk_level):
        """Generates a plain-English explanation for a flagged clause using Gemini."""
        prompt = f"""
        You are a legal expert specializing in contract risk assessment. 
        The following legal clause has been flagged as having a '{risk_level}' risk level.
        
        Legal Clause:
        "{clause_text}"
        
        Task:
        1. Explain why this clause is considered '{risk_level}' risk in plain English.
        2. Identify potential financial or legal obligations/liabilities.
        3. Suggest a simple way to mitigate this risk (e.g., standard wording or points to negotiate).
        
        Keep the response concise, professional, and easy for a non-expert to understand.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating explanation: {str(e)}"

if __name__ == "__main__":
    # Example usage
    # explainer = RiskExplainer()
    # explanation = explainer.generate_explanation("The vendor shall be liable for all indirect damages...", "High")
    # print(explanation)
    pass
