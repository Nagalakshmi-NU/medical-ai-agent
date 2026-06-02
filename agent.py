import os
from dotenv import load_dotenv
from google import genai

# 1. Unlock our secret Gemini Key
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# --- THE MAIN PROGRAM ---
print("1. Uploading the messy PDF directly to Gemini's 'eyes'...")

# 2. Hand the file directly to Google Gemini
patient_file = client.files.upload(file="patient 2 (1).pdf")

print("2. Sending instructions to the AI Brain...")

# 3. Set up the strict rules 
prompt = """
You are a strict medical assistant creating a Discharge Summary Draft. 
Read the attached clinical notes and extract the following information exactly as it appears. 

The Golden Rule: You must NEVER guess or make things up. If any piece of information is not in the text, or if a lab result is still waiting, you must explicitly write 'Missing or Pending'. 

Please provide the summary in this exact list format:
- Patient Demographics (Age/Gender/Weight):
- Admission & Discharge Dates:
- Principal & Secondary Diagnoses:
- Hospital Course (brief summary of what happened):
- Procedures Done:
- Discharge Medications (Note any new medicines added):
- Allergies:
- Follow-up Instructions:
- Pending Results:
- Discharge Condition:
"""

# 4. Get the answer by giving the AI both the FILE and the PROMPT
ai_response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=[patient_file, prompt]
)

print("\n--- AI SUMMARY ---")
print(ai_response.text)