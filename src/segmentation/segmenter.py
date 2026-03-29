import re
import pdfplumber
import spacy

class ContractSegmenter:
    def __init__(self):
        # Using spacy for better sentence/clause boundary detection
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            # If not installed, download it
            import subprocess
            import sys
            subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
            self.nlp = spacy.load("en_core_web_sm")

    def extract_text(self, file_path):
        """Extracts text from a PDF or TXT file."""
        text = ""
        if file_path.lower().endswith('.pdf'):
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        elif file_path.lower().endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        else:
            raise ValueError("Unsupported file format. Provide a PDF or TXT file.")
        return text

    def segment_into_clauses(self, text):
        """Segments contract text into individual clauses based on common numbering patterns and line breaks."""
        # Common contract clause numbering patterns (e.g., 1., 1.1, Article 1, Section 1)
        patterns = [
            r'^\d+\.\s+',               # 1. 
            r'^\d+\.\d+\s+',            # 1.1
            r'^Article\s+\d+',          # Article 1
            r'^Section\s+\d+',          # Section 1
            r'^[A-Z][a-z]+\s+\d+\.\d+', # Clause 1.1
            r'^\([a-z]\)\s+',           # (a)
            r'^\([ivx]+\)\s+'           # (i), (ii)
        ]
        
        # Split by potential clause boundaries (lines starting with a pattern)
        # We also look for empty lines as potential separators
        lines = text.split('\n')
        clauses = []
        current_clause = ""

        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            is_new_clause = any(re.match(p, line, re.IGNORECASE) for p in patterns)
            
            if is_new_clause and current_clause:
                clauses.append(current_clause.strip())
                current_clause = line
            else:
                current_clause += " " + line

        if current_clause:
            clauses.append(current_clause.strip())

        # Further refinement: if a clause is too long, it might be multiple clauses without numbering
        # We can use spacy to break down very long segments if needed, but for now, we'll keep it simple.
        
        return clauses

if __name__ == "__main__":
    # Example usage (can be tested if a PDF is provided)
    # segmenter = ContractSegmenter()
    # text = segmenter.extract_text_from_pdf("sample.pdf")
    # clauses = segmenter.segment_into_clauses(text)
    # for i, clause in enumerate(clauses):
    #     print(f"Clause {i+1}: {clause[:100]}...")
    pass
