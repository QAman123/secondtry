import streamlit as st
from resume_generator import generate_resume_and_cover_letter

st.set_page_config(page_title="Resume & Cover Letter Generator", layout="centered")
st.title("🧠 Resume & Cover Letter Generator")

with st.form("resume_form"):
    name = st.text_input("Full Name")
    job_title = st.text_input("Job Title")
    summary = st.text_area("Professional Summary")
    skills = st.text_input("Skills (comma-separated)")
    experience = st.text_area("Experience")
    education = st.text_area("Education")
    submitted = st.form_submit_button("Generate")

if submitted:
    if all([name, job_title, summary, skills, experience, education]):
        try:
            with st.spinner("Generating..."):
                resume, cover_letter = generate_resume_and_cover_letter(
                    name, job_title, summary, skills, experience, education
                )
            st.subheader("📄 Resume")
            st.code(resume, language="markdown")
            st.subheader("✉️ Cover Letter")
            st.code(cover_letter, language="markdown")
        except Exception as e:
            st.error(f"❌ Error: {e}")
    else:
        st.warning("Please fill in all the fields.")
