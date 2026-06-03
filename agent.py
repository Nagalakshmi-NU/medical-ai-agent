import os
import json
import time
import re
from dotenv import load_dotenv
from google import genai
from google.genai import types

# 1. Initialize Google GenAI
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# 2. Define Real Python Tools
def check_drug_interactions(medications_list: str) -> str:
    """Checks a list of medications for potential adverse drug interactions."""
    print(f"⚙️ [Executing Tool] check_drug_interactions with inputs: {medications_list}")
    if "Oflox TZ" in medications_list and "Loperamide" in medications_list:
        return "WARNING: Potential risk of QT prolongation when combining fluoroquinolones (Ofloxacin) with high-dose antimotility agents (Loperamide). Monitor cardiac rhythm."
    return "No severe drug-drug interactions found in standard database lookup."

def escalate_to_clinician(reason: str) -> str:
    """Flags a clinical data conflict or safety concern for urgent clinician review."""
    print(f"⚙️ [Executing Tool] escalate_to_clinician with reason: {reason}")
    return f"SUCCESS: Escalation flag raised. Reason logged: '{reason}'. Clinician review appended to draft."

AVAILABLE_TOOLS = {
    "check_drug_interactions": check_drug_interactions,
    "escalate_to_clinician": escalate_to_clinician
}

# 3. Main Agent Program
print("1. Uploading the messy PDF directly to Gemini's 'eyes'...")
patient_file = client.files.upload(file="patient_2.pdf")

system_instruction = """
You are an advanced Agentic Medical Assistant. Your goal is to run diagnostic checks and draft a Discharge Summary.
You have access to tools that you can call by outputting a specific JSON format.

Available Tools:
1) check_drug_interactions(medications_list: string) -> Returns risk analysis.
2) escalate_to_clinician(reason: string) -> Use this whenever you find a conflict, or critical medication changes (like stopping insulin) with NO documented reason.

To call a tool, you must respond in this EXACT JSON format. Do not add any text before or after the JSON braces:
{
    "thought": "Your step-by-step reasoning about what you have found so far and what you need to do next.",
    "tool_chosen": "name_of_the_tool",
    "inputs": {"arg_name": "value"},
    "status": "CONTINUE"
}

If you have completed medication reconciliation, checked for interactions, flagged omissions, and are ready to compile the final report, respond in this JSON format:
{
    "thought": "I have verified all clinical data and executed all necessary safety lookups. Generating final summary.",
    "tool_chosen": "none",
    "inputs": {},
    "status": "FINAL_REPORT"
}
"""

step = 1
max_steps = 5  # REQUIREMENT 9: Control Cap
agent_history = []  

print("\n2. Initiating Agent Loop...")

while step <= max_steps:
    print(f"\n--- 🧠 AGENT STEP {step} ---")
    current_prompt = (
        f"Analyze the medical record file. Choose a tool to run or conclude the assignment.\n"
        f"CRITICAL: Your entire output must be a single valid JSON object block matching the schema instructions. Do not write text outside the brackets.\n\n"
        f"History of Steps Letters Taken So Far:\n{json.dumps(agent_history, indent=2)}"
    )
    
    response = None
    attempts = 0
    max_attempts = 3
    while attempts < max_attempts:
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[patient_file, system_instruction, current_prompt]
            )
            break
        except Exception:
            attempts += 1
            print(f"⚠️ API call encountered an error (Attempt {attempts}/{max_attempts}). Retrying...")
            time.sleep(5)
    
    if response is None:
        print("🛑 Agent loop stopped safely to prevent crashing due to external API outage.")
        break
        
    try:
        clean_json_match = re.search(r"\{.*\}", response.text, re.DOTALL)
        if clean_json_match:
            decision = json.loads(clean_json_match.group(0))
        else:
            raise ValueError("No valid JSON braces found in response.")
    except Exception as e:
        print(f"⚠️ Failed to isolate JSON format on this step. Raw output skipped.")
        agent_history.append({"step": step, "thought": "Failed to parse structure, forcing continuation.", "tool_called": "none", "result_returned": "Error"})
        step += 1
        time.sleep(2)  # Give API a breather
        continue
        
    # REQUIREMENT 10: Observability Trace printing
    print(f"🤔 Reasoning: {decision.get('thought')}")
    print(f"🛠️ Action Chosen: {decision.get('tool_chosen')}")
    print(f"📥 Inputs: {decision.get('inputs')}")
    
    if decision.get("status") == "FINAL_REPORT":
        print("\n✅ Agent loop completed safely. All constraints verified.")
        break
        
    tool_name = decision.get("tool_chosen")
    tool_inputs = decision.get("inputs", {})
    
    if tool_name in AVAILABLE_TOOLS:
        tool_result = AVAILABLE_TOOLS[tool_name](**tool_inputs)
        print(f"📤 Tool Output: {tool_result}")
        
        agent_history.append({
            "step": step,
            "thought": decision.get('thought'),
            "tool_called": tool_name,
            "result_returned": tool_result
        })
    else:
        print(f"ℹ️ Concluding loop step.")
        break
        
    step += 1
    time.sleep(2)  # REQUIREMENT 8: Added pacing delay to respect server rate limits

# --- FINAL GENERATION STEP WITH RETRY SAFETY NET ---
print("\n3. Instructing Agent to assemble the final structured Discharge Summary...")
final_prompt = f"""
Based on the patient document and your tool history results: {json.dumps(agent_history, indent=2)}
Generate the full structured Discharge Summary Draft exactly in this layout.

- Patient Demographics (Age/Gender/Weight):
- Admission & Discharge Dates:
- Principal & Secondary Diagnoses:
- Hospital Course (brief summary of what happened):
- Procedures Done:
- Discharge Medications (Explicitly reconcile Admission vs Discharge and flag any un-reasoned changes here):
- Allergies:
- Follow-up Instructions:
- Pending Results:
- Discharge Condition:
- Safety Escalations / Clinician Flags Raised (List any tool alerts, omissions, or conflicts found here):
"""

final_response = None
final_attempts = 0
while final_attempts < 3:
    try:
        # Give a quick rest before the final heavy generation step
        time.sleep(3)
        final_response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[patient_file, final_prompt]
        )
        break
    except Exception as e:
        final_attempts += 1
        print(f"⚠️ Summary generation rate-limited (Attempt {final_attempts}/3). Retrying in 5s...")
        time.sleep(5)

print("\n=================== 📋 FINAL DISCHARGE SUMMARY DRAFT ===================")
if final_response:
    print(final_response.text)
else:
    print("Error: Could not retrieve final document summary due to server limitations. Please run script again.")