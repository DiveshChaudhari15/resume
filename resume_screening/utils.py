from PyPDF2 import PdfReader

def extract_text_from_pdf(file):
    """Extract text from a PDF file."""
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def extract_skills(resume_text):
    """Extract skills from resume text."""
    skills = ["Python", "Java", "SQL", "HTML", "CSS", "JavaScript", "Flask", "MongoDB"]
    extracted_skills = [skill for skill in skills if skill.lower() in resume_text.lower()]
    return extracted_skills

def categorize_resume(resume_text):
    """Categorize the resume based on keywords."""
    if "developer" in resume_text.lower():
        return "Developer"
    elif "analyst" in resume_text.lower():
        return "Analyst"
    else:
        return "Other"

def save_to_db(filename, text, skills, category, collection):
    """Save resume data to MongoDB."""
    collection.insert_one({
        "filename": filename,
        "text": text,
        "skills": skills,
        "category": category
    })

def get_skill_analysis(collection):
    """Analyze skills data from the database."""
    skill_counts = {}
    resumes = collection.find({}, {"skills": 1, "_id": 0})
    for resume in resumes:
        for skill in resume['skills']:
            skill_counts[skill] = skill_counts.get(skill, 0) + 1
    return skill_counts
