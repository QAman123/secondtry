import os
import streamlit as st
from openai import OpenAI
from io import BytesIO
from docx import Document
import fitz  # PyMuPDF for PDF text extraction
import difflib
from docx import Document
from io import BytesIO
from fpdf import FPDF

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def clean_text(text):
    replacements = {
        '\u2013': '-', '\u2014': '-',
        '\u2018': "'", '\u2019': "'",
        '\u201c': '"', '\u201d': '"',
        '\u2026': '...',
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text


def create_pdf(adapted_resume, cover_letter):
    adapted_resume = clean_text(adapted_resume)
    cover_letter = clean_text(cover_letter)

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Resume Page
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Adapted Resume", ln=True)
    pdf.set_font("Arial", '', 12)
    for line in adapted_resume.split('\n'):
        pdf.multi_cell(0, 8, line)

    # Cover Letter Page
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Cover Letter", ln=True)
    pdf.set_font("Arial", '', 12)
    for line in cover_letter.split('\n'):
        pdf.multi_cell(0, 8, line)

    # Generate PDF as bytes
    pdf_bytes = pdf.output(dest='S').encode('latin-1')
    return BytesIO(pdf_bytes)



def create_docx(adapted_resume, cover_letter):
    doc = Document()
    doc.add_heading("Adapted Resume", level=1)
    for line in adapted_resume.split('\n'):
        doc.add_paragraph(line)

    doc.add_page_break()

    doc.add_heading("Cover Letter", level=1)
    for line in cover_letter.split('\n'):
        doc.add_paragraph(line)

    # Save to in-memory BytesIO
    doc_stream = BytesIO()
    doc.save(doc_stream)
    doc_stream.seek(0)
    return doc_stream

def get_diff(original_text, updated_text):
    original_lines = original_text.splitlines()
    updated_lines = updated_text.splitlines()

    diff = difflib.unified_diff(
        original_lines,
        updated_lines,
        fromfile="Original Resume",
        tofile="Adapted Resume",
        lineterm=""
    )
    return "\n".join(diff)



def extract_text_from_pdf(uploaded_file):
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text


def extract_text_from_docx(file):
    try:
        doc = Document(file)
        fullText = []
        for para in doc.paragraphs:
            fullText.append(para.text)
        return "\n".join(fullText).strip()
    except Exception as e:
        st.error(f"Error reading DOCX: {e}")
        return None

def extract_resume_text(uploaded_file):
    if uploaded_file.type == "application/pdf":
        return extract_text_from_pdf(uploaded_file)
    elif uploaded_file.type in [
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/msword",
    ]:
        return extract_text_from_docx(uploaded_file)
    else:
        st.error("Unsupported file type. Please upload PDF or DOCX.")
        return None

def generate_adapted_resume_and_cover(job_desc, resume_text):
    system_prompt = (
        "You are an expert career coach and resume writer.\n"
        "Adapt the candidate's resume to better fit the job description.\n"
        "Then write a personalized cover letter highlighting relevant skills.\n"
        "Output both clearly separated with the headings:\n"
        "=== Adapted Resume ===\n"
        "and\n"
        "=== Cover Letter ==="
    )
    user_prompt = (
        f"Job Description:\n{job_desc}\n\nCandidate Resume:\n{resume_text}\n\n"
        "Please provide:\n1) Adapted Resume\n2) Cover Letter\n\n"
        "Separate them exactly using the headings."
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=3000,
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()

def split_output(output_text):
    adapted_resume = ""
    cover_letter = ""

    # Try splitting by headings exactly as requested
    if "=== Adapted Resume ===" in output_text and "=== Cover Letter ===" in output_text:
        parts = output_text.split("=== Cover Letter ===")
        adapted_resume = parts[0].replace("=== Adapted Resume ===", "").strip()
        cover_letter = parts[1].strip()
    else:
        # fallback: no clear split, put all in adapted_resume
        adapted_resume = output_text

    return adapted_resume, cover_letter

st.title("Resume & Cover Letter Tailor")

st.markdown("Paste the **Job Description** below:")
job_desc = st.text_area("Job Description", height=200)

uploaded_file = st.file_uploader("Upload your Resume (PDF or DOCX)", type=["pdf", "docx"])

if uploaded_file:
    resume_text = extract_resume_text(uploaded_file)
    if resume_text:
        st.subheader("Extracted Resume Text Preview")
        st.text_area("Resume Text", resume_text[:8000], height=300)

        if st.button("Generate Adapted Resume & Cover Letter"):
            with st.spinner("Generating..."):
                output = generate_adapted_resume_and_cover(job_desc, resume_text)
                adapted_resume, cover_letter = split_output(output)

            st.subheader("Adapted Resume")
            st.text_area("", adapted_resume, height=600)

            st.subheader("Cover Letter")
            st.text_area("", cover_letter, height=600)



            # Show diff
            diff_text = get_diff(resume_text, adapted_resume)
            st.subheader("Difference between Original and Adapted Resume (unified diff)")
            st.code(diff_text, language="diff", line_numbers=True)

            docx_file = create_docx(adapted_resume, cover_letter)
            pdf_file = create_pdf(adapted_resume, cover_letter)

            st.download_button(
                label="📄 Download PDF",
                data=pdf_file,
                file_name="Adapted_Resume_and_Cover_Letter.pdf",
                mime="application/pdf"
            )

            st.download_button(
                label="Download Adapted Resume & Cover Letter as DOCX",
                data=docx_file,
                file_name="adapted_resume_and_cover_letter.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )


else:
    st.info("Please upload a resume to continue.")
