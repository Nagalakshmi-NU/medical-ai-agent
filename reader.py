import PyPDF2

def read_patient_pdf(file_name):
    # 1. Create an empty bucket to hold our words
    all_text = ""
    
    # 2. Open the PDF file safely
    with open(file_name, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        
        # 3. Read every single page and pour the words into the bucket
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                all_text += page_text + "\n"
                
    return all_text

# --- Let's test it out! ---
my_text = read_patient_pdf("patient 2 (1).pdf")

# Print out the first 500 characters just to prove it worked
print("--- PDF TEXT EXTRACTED SUCCESSFULLY ---")
print(my_text[:500])