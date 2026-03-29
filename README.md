# LEXSCORE: Legal Clause Risk Scorer

<div align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/PyTorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white" alt="PyTorch"/>
  <img src="https://img.shields.io/badge/HuggingFace-F1DE4F?style=for-the-badge&logo=huggingface&logoColor=black" alt="HuggingFace"/>
  <img src="https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB" alt="React"/>
  <img src="https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white" alt="Vanilla CSS"/>
  <img src="https://img.shields.io/badge/Gemini-8E75B2?style=for-the-badge&logo=google&logoColor=white" alt="Gemini AI"/>
</div>

<br/>

## Overview

**LexScore** is an intelligent, full-stack legal document analysis platform. Designed with a striking "Legal Brutalism" UX, the system parses contract files natively, extracts individual legal clauses, and uses a fine-tuned **LegalBERT** model to instantly flag clauses carrying anomalous legal, financial, or organizational risk. 

It provides detailed risk metrics, visual heat-map source text extraction, and **Gemini AI**-powered "Plain English" explanations for complex legal jargon.

## Key Features

- **GPU-Accelerated Inference**: Evaluates large contracts (PDF or TXT) clause-by-clause almost instantly using PyTorch and FastAPI.
- **Three-Tier Classification System**: Automatically identifies and categorizes semantic risks dynamically (High, Medium, Low) using deep learning.
- **Generative Summarization**: Leverages large language models (LLMs) to instantly summarize and explain dense, high-risk legal clauses to laymen users.
- **Legal Brutalism UI**: A stark, highly-responsive frontend built in React, utilizing Native CSS scroll snapping, dark/light dynamic theme inversion, and Framer Motion context animations.
- **Visual Analytics**: Interactive Recharts pie and bar graphs detailing the breakdown of classified risks across the entire document.

## System Architecture

### Backend (Python)
- **API Engine:** FastAPI
- **Document Parsing:** `pdfplumber` and `spacy` for rigorous NLP sentence segmentation and clause boundary detection.
- **Machine Learning Core:** HuggingFace `transformers` running a fine-tuned `nlpaueb/legal-bert-base-uncased` checkpoint trained over the **CUAD** (Contract Understanding Atticus Dataset).
- **Explanation Layer:** Google Gemini AI API integration for human-readable translation.

### Frontend (React)
- **Framework:** React / Vite
- **Styling:** Vanilla CSS Custom Variables (Dynamic styling overriding)
- **Animations:** Framer Motion
- **Charting:** Recharts

## Getting Started

### 1. Start the Backend API
Navigate to the root and install the required machine-learning dependencies:
```bash
cd src
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

Ensure you have your environment variables set correctly locally (like your Gemini API Key in `.env`), then run the application server:
```bash
python main.py
```
*The API will boot up and handle inferences on `http://localhost:8001`*

### 2. Start the Frontend Interface
In a new terminal window, boot up the React application:
```bash
cd frontend
npm install
npm run dev
```
*The web app will boot up in your browser where you can immediately drag and drop sample contracts.*

---
*Developed as part of an experimental NLP Research Project @ PSG TECH.*
