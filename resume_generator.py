import os
from huggingface_hub import InferenceClient

def generate_resume_and_cover_letter(name, job_title, summary, skills, experience, education):
    hf_api_key = os.getenv("HF_API_KEY")
    if not hf_api_key:
        raise ValueError("Missing Hugging Face API key. Please set the HF_API_KEY environment variable.")

    client = InferenceClient(
        provider="cohere",
        api_key=hf_api_key,
    )

    prompt = f"""
    Create a professional resume and a personalized cover letter based on the following:
    Name: {name}
    Job Title: {job_title}
    Summary: {summary}
    Skills: {skills}
    Experience: {experience}
    Education: {education}

    Format:
    RESUME:
    ...
    COVER LETTER:
    ...
    """

    completion = client.chat.completions.create(
        model="CohereLabs/aya-expanse-8b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
    )

    text = completion.choices[0].message['content']

    if "COVER LETTER:" in text:
        resume_text, cover_letter_text = text.split("COVER LETTER:", 1)
        resume_text = resume_text.replace("RESUME:", "").strip()
        cover_letter_text = cover_letter_text.strip()
    else:
        resume_text = text.strip()
        cover_letter_text = "(Cover letter not found in response.)"

    return resume_text, cover_letter_text
