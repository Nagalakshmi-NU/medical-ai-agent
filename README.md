# Multimodal Agentic AI System for Clinical Discharge Summaries

**Author:** Nagalakshmi N U  
**Role:** AI Engineer
**Target Focus:** Part 1 — Comprehensive Discharge Summary Agent Loop (Production-Grade)

---

## 📌 Project Overview
This project implements a clinical AI agent designed to extract information from highly unstructured, messy, and hand-written clinical source notes (PDFs) and generate a structured, clinically safe discharge summary draft. 

Instead of relying on a fragile, single LLM prompting pipeline, this architecture implements a true **ReAct (Reasoning + Acting) Agent Loop**. The agent acts as an autonomous clinical investigator—dynamically assessing documents, executing diagnostic Python tools, logging its inner monologues, recovering from external API failures, and strictly enforcing zero-fabrication guardrails.

---

## 🧠 1. Agent's Loop Design
The core architecture is built on a dynamic ReAct loop governed by a state-tracking `while` loop (capped at `max_steps = 5` to prevent infinite runtime). 
* **Reasoning & Action:** At each step, the agent analyzes the medical document alongside its historical trace of previous actions. It must output a strict JSON schema containing its `thought` process, the `tool_chosen`, and the `inputs`.
* **Tool Execution:** The agent autonomously routes data to Python tools (e.g., `check_drug_interactions` or `escalate_to_clinician`) based on its reasoning. 
* **Observability:** The system emits a transparent, live trace to the terminal at every turn, detailing its reasoning and tool outputs before compiling the final summary.

## 🛡️ 2. Enforcing the "No Fabrication" Guardrail
In a clinical setting, hallucination is dangerous. This guardrail is enforced through strict system prompts and the overarching Golden Rule: **Only extract, never infer.** * When demographic data (like exact age or gender) is missing from the source text, the agent is instructed to explicitly output `Not explicitly documented` rather than guessing based on context. 
* By forcing the agent to log its reasoning *before* taking action or generating the final report, the system grounds its output entirely in the verified tool history and the uploaded PDF context.

## ⚠️ 3. Handling Failures and Conflicts
The system is built to be highly resilient to both technical failures and clinical data conflicts:
* **Technical Failures:** It features RegEx-based block isolation to parse tool commands even if the LLM wraps the JSON in conversational text. It also utilizes automated `try-except` retry loops with pacing delays (`time.sleep`) to successfully navigate 503 Server Unavailable blips or 429 Rate Limit spikes without crashing.
* **Clinical Conflicts:** The agent actively reconciles admission versus discharge states. When it detects dangerous omissions—such as a patient's vital insulin regimen being stopped without a documented reason, or a discharge diagnosis contradicting a lab culture—it autonomously triggers the `escalate_to_clinician` tool to flag these contradictions in the final report.

## 📊 4. Part 2: Reward Design and Results
*Note: My engineering submission is specifically focused on building a robust, production-grade ReAct loop for Part 1. However, if designing a Reinforcement Learning (RLHF) reward model for this system, my approach would be:*
* **High Penalty (-1.0):** For any hallucination of demographic data, vitals, or clinical diagnoses.
* **High Reward (+1.0):** For autonomously utilizing the `escalate_to_clinician` tool when dangerous conflicting discharge medications (like the omitted insulin) or contradictory lab results are detected.
* **Moderate Reward (+0.5):** For strict adherence to the requested JSON formatting and successfully completing the loop within the step constraints.

## 🚧 5. Limitations of the Approach
While highly resilient, the current architecture has a few known limitations:
* **Token & Network Constraints:** Processing massive, multi-page PDFs in a single API call can lead to free-tier rate limits or network SSL timeouts. To maintain stability, the system sometimes requires text compression (focusing on admission and discharge sections), which risks omitting nuances buried in the middle pages.
* **Tool Naivety:** The current `check_drug_interactions` tool relies on simulated logic rather than a live pharmacological database API, limiting its real-world clinical power.
* **Single-Point Bottleneck:** The final generation step relies on a single prompt to synthesize the tool history and output the draft. If the API fails on this final step, the summary is lost despite successful prior reasoning.

## 🔮 6. What I Would Do With More Time
If given more time to scale this system for production, I would implement the following:
1. **Retrieval-Augmented Generation (RAG):** Instead of passing an entire 71-page document at once, I would chunk the PDF and use vector embeddings to retrieve only the most relevant clinical sections, solving the context window and network timeout issues.
2. **Multi-Agent Validation:** I would introduce a secondary "Critic Agent" whose sole job is to review the primary agent's final draft against the source text to double-check for hallucinations and ensure strict formatting compliance before presenting it to the user.
3. **Live Clinical API Integration:** Connect the tool functions to real healthcare databases (like RxNorm or SNOMED CT) for dynamically accurate drug interaction checks and standardized medical coding.

---

## 🚀 Setup & Execution Instructions

### 1. Environment Installation
Clone or unzip this project folder, navigate inside the root directory using your terminal, and configure a clean Python virtual environment:

python -m venv env
.\env\Scripts\activate

### 2. Dependency Resolution
Install the required packages using the official updated libraries:

pip install google-genai python-dotenv PyPDF2

### 3. Secret Token Injection
Create a `.env` configuration file in the primary directory (this is securely tracked and blocked from remote public uploads via our local `.gitignore` rules):

GEMINI_API_KEY=your_actual_secret_developer_api_key_here

### 4. Running the Agent
Execute the master process. You will see the agent's real-time step trace print directly to your screen before it outputs the final summary:

python agent.py
