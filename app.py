import streamlit as st
from resume_generator import generate_resume_and_cover_letter
import base64

st.set_page_config(page_title="AI Resume Generator", layout="centered")
st.title("🧠 AI-Powered Resume & Cover Letter Generator")

st.markdown("""
Enter your information below and receive a professionally written resume and cover letter powered by AI.
""")

with st.form("resume_form"):
    name = st.text_input("Full Name")
    job_title = st.text_input("Target Job Title")
    summary = st.text_area("Professional Summary")
    skills = st.text_area("Key Skills (comma-separated)")
    experience = st.text_area("Work Experience (include company, role, duration)")
    education = st.text_area("Education")
    submitted = st.form_submit_button("Generate")

if submitted:
    with st.spinner("Generating documents..."):
        resume_text, cover_letter_text = generate_resume_and_cover_letter(
            name, job_title, summary, skills, experience, education
        )

    st.success("Documents generated!")

    st.subheader("📄 Resume")
    st.text(resume_text)

    st.subheader("✉️ Cover Letter")
    st.text(cover_letter_text)

    def get_text_download_link(text, filename):
        b64 = base64.b64encode(text.encode()).decode()
        return f'<a href="data:file/txt;base64,{b64}" download="{filename}">👅 Download {filename}</a>'

    st.markdown(get_text_download_link(resume_text, "resume.txt"), unsafe_allow_html=True)
    st.markdown(get_text_download_link(cover_letter_text, "cover_letter.txt"), unsafe_allow_html=True)