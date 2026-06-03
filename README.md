# Multimodal Agentic AI System for Clinical Discharge Summaries

**Author:** Nagalakshmi N U  
**Role:** AI Engineer Assignment Submission  
**Target Focus:** Part 1 — Comprehensive Discharge Summary Agent Loop (Production-Grade)

---

## 📌 Project Overview
This project implements a clinical AI agent designed to extract information from highly unstructured, messy, and hand-written clinical source notes (PDFs) and generate a structured, clinically safe discharge summary draft. 

Instead of relying on a fragile, single LLM prompting pipeline, this architecture implements a true **ReAct (Reasoning + Acting) Agent Loop**. The agent acts as an autonomous clinical investigator—dynamically assessing documents, executing diagnostic Python tools, logging its inner monologues, recovering from external API failures, and strictly enforcing zero-fabrication guardrails.

---

## 🛠️ Mapping to Hard Requirements

The system completely satisfies 100% of the hard constraints outlined in the Part 1 assignment evaluation brief:

1. **A Real Agent Loop:** Implemented via an internal runtime evaluation block (`while step <= max_steps`). The agent dynamically assesses previous historical steps to decide whether to continue tracking clinical elements or proceed to compile the report.
2. **PDF Ingestion:** Leverages Gemini's advanced multimodal engine (`client.files.upload`) to process complex, multi-page medical images and charts natively without brittle text OCR parsing.
3. **No Fabrication (The Core Guardrail):** Enforces a strict "Golden Rule" via system parameters. When demographic information (e.g., patient age) is missing from source text layers, the system explicitly logs `Not explicitly documented` instead of guessing.
4. **Pending/Missing Data Handling:** Identifies outstanding lab protocols (such as unreturned urine culture wait times) and routes them specifically into a designated `Pending Results` module.
5. & 6. **Medication Reconciliation & Conflict Detection:** The agent actively checks differences between entry states and discharge orders. It successfully isolates and escalates critical real-world omissions—such as the cessation of a patient's vital home/ward insulin and thyroid regimens without a documented clinical reason.
7. **Autonomous Tool Selection:** Provides the agent access to operational Python methods:
   - `check_drug_interactions(medications_list)`: Simulates database checks for drug-drug interactions.
   - `escalate_to_clinician(reason)`: Formally raises safety flags for critical data contradictions or omissions.
8. **Robust Failure Handling:** Built to withstand external server failures. The code implements regular expression string extraction to isolate JSON formats from loose conversational text blocks. It also contains automated `try-except` retry loops with pacing delays (`time.sleep`) to successfully navigate through temporary 503 Server Unavailable blips or 429 Rate Limit spikes without crashing.
9. **Control Cap:** Implements a hard control threshold ceiling (`max_steps = 5`) to prevent runtime infinite loops and control costs.
10. **Observability Trace:** Emits a completely transparent trace live to the terminal screen at every turn using the following clear structural layout:
    `🧠 AGENT STEP` -> `🤔 Reasoning` -> `🛠️ Action Chosen` -> `📥 Inputs` -> `📤 Tool Output`

---

## 🏗️ Technical Architecture
- **Language:** Python 3.12+
- **AI Core:** Google GenAI SDK (utilizing the state-of-the-art multimodal vision model `gemini-2.5-flash`)
- **State Pattern:** JSON-driven ReAct loop with historical tracking arrays.
- **Resilience Engine:** RegEx-based block isolation combined with back-off retry logic.

---

## 🚀 Setup & Execution Instructions

### 1. Environment Installation
Clone or unzip this project folder, navigate inside the root directory using your terminal, and configure a clean Python virtual environment:

python -m venv env
.\env\Scripts\Activate.ps1


### 2. Dependency Resolution
Install the required packages using the official updated libraries:

pip install google-genai python-dotenv


### 3. Secret Token Injection
Create a `.env` configuration file in the primary directory (this is securely tracked and blocked from remote public uploads via our local `.gitignore` rules):

GEMINI_API_KEY=your_actual_secret_developer_api_key_here


### 4. Running the Agent
Execute the master process. You will see the agent's real-time step trace print directly to your screen before it outputs the final summary:

python agent.py