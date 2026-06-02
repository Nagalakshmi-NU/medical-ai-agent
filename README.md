# Discharge Summary AI Agent 
**Author:** Nagalakshmi N U
**Role:** AI Engineer Take-Home Assignment (Dscribe / Unriddle Technologies)

## 📌 Overview
This repository contains an agentic AI system designed to read messy, unstructured, and often incomplete clinical source notes (PDFs) and generate a structured, clinically safe Discharge Summary Draft. 

The core philosophy of this agent is **Clinical Safety Above All**. It is explicitly designed to refuse to invent facts, actively flagging missing or pending information for clinician review.

## 🏗️ Agent Design & Loop Architecture
During initial data exploration, it became clear that standard PDF extraction libraries (like `PyPDF2` or `PyMuPDF`) failed to capture the data accurately because the synthetic medical records mimic real-world scanned documents, handwriting, and complex tabular charts. 

Instead of building a brittle OCR pipeline, this agent leverages a **Multimodal Vision Architecture** using Google Gemini 2.5 Flash. 

**The Loop:**
1. **Ingestion:** The agent directly uploads the raw PDF document into the multimodal context window.
2. **Analysis & Structuring:** A highly constrained system prompt acts as the "Brain," forcing the model to act as a strict data extractor rather than a conversational chatbot.
3. **Draft Generation:** The agent structures the extracted data into the required 10-point clinical format.

## 🛡️ Enforcing the No-Fabrication Guardrail
The most critical requirement of this system is the prevention of hallucinations. This is enforced via the **Golden Rule Guardrail** injected directly into the system prompt:
> *"The Golden Rule: You must NEVER guess or make things up. If any piece of information is not in the text, or if a lab result is still waiting, you must explicitly write 'Missing or Pending'."*

**Proof of Concept:** When tested on Patient 2, the source notes lacked explicitly stated Age and Gender. Instead of guessing based on context clues, the agent successfully outputted:
* Age: Missing
* Gender: Missing
This ensures the output remains a safe draft for clinician review, never an auto-finalized document.

## ⚠️ Handling Failures and Conflicts
* **Missing/Pending Data:** Addressed via the Golden Rule prompt. The agent explicitly flags items like "Urine culture and sensitivity report - Pending".
* **API/System Failures:** The current script relies on the provider's native error handling. In a production environment, this would be wrapped in a robust `try-except` block with exponential backoff using the `tenacity` library to handle rate limits (429s) or temporary API outages (503s).

## 🚀 Limitations & What I Would Do With More Time
Due to the 48-hour time-box, this submission focuses on delivering a highly robust **Part 1**. 

**Current Limitations:**
* **Single-Pass Extraction:** Currently, the system uses a single multimodal call. While highly effective for these PDFs, extremely long patient histories (hundreds of pages) could overwhelm the context window or cause "lost in the middle" phenomena.
* **Implicit Conflict Resolution:** The agent relies on its internal logic to surface conflicts. 

**What I'd Do Next (Implementing Part 2 - Learning from Edits):**
If given more time, I would build the feedback loop required in Part 2 using **Dynamic In-Context Learning (RAG for Edits)**:
1. **The Reward Signal:** I would define the reward metric as the normalized Levenshtein edit distance between the agent's initial draft and the doctor's finalized version. 
2. **The Feedback Loop:** When a doctor edits a draft, the original text, the agent's draft, and the doctor's correction would be embedded and stored in a vector database (like ChromaDB).
3. **Continuous Improvement:** On future runs, the agent would first query the database for similar past corrections. The prompt would dynamically include these as few-shot examples (e.g., *"In the past, you missed this specific medication change. Pay close attention to X"*). This allows the agent to adapt to a specific hospital's or doctor's style without requiring expensive model fine-tuning, keeping the Part 1 safety guarantees completely intact.

## 💻 Run Instructions

**1. Install Dependencies**
pip install google-genai python-dotenv

**2. Environment Setup**
Create a .env file in the root directory and add your API key:
GEMINI_API_KEY="your_api_key_here"

**3. Run the Agent**
Place the patient PDF in the root folder and run:
python agent.py