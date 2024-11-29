import matplotlib
matplotlib.use('Agg')  # Set the backend to Agg for non-GUI plotting

import os
from flask import Flask, render_template, request, jsonify
import pdfplumber
import matplotlib.pyplot as plt
import io
import base64
from pymongo import MongoClient

# Flask app initialization
app = Flask(__name__)

# MongoDB Configuration
client = MongoClient("mongodb://localhost:27017/")  # Connect to MongoDB
db = client["resume_screening"]                    # Database name
resumes_collection = db["resumes"]                 # Collection name

# File upload settings
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'docx', 'txt'}

# Skills categories for analysis
skills_categories = {
    "Programming Languages": ['python', 'java', 'c', 'ruby', 'javascript', 'sql'],
    "Web Development": ['html', 'css', 'flask', 'react', 'angular', 'vue'],
    "Soft Skills": ['communication', 'teamwork', 'leadership', 'problem-solving', 'creativity']
}

# Helper function to check allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Helper function to extract text from a PDF file
def extract_text_from_pdf(file_path):
    with pdfplumber.open(file_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text

# Helper function to analyze resume content
def analyze_resume(resume_text):
    skill_count = {category: 0 for category in skills_categories}
    for category, skills in skills_categories.items():
        for skill in skills:
            skill_count[category] += resume_text.lower().count(skill)
    total_score = sum(skill_count.values())
    return skill_count, total_score

# Route for homepage
@app.route('/')
def index():
    return render_template('index.html')

# Route to upload and analyze the resume
@app.route('/upload', methods=['POST'])
def upload_resume():
    if 'resume' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['resume']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = file.filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Extract text from the uploaded resume
        try:
            resume_text = extract_text_from_pdf(file_path)
        except Exception as e:
            return jsonify({"error": f"Error reading file: {str(e)}"}), 500

        # Analyze the resume content
        skill_count, total_score = analyze_resume(resume_text)

        # Generate a pie chart for skills distribution
        categories = list(skill_count.keys())
        scores = list(skill_count.values())

        img = io.BytesIO()
        plt.figure(figsize=(6, 6))
        plt.pie(scores, labels=categories, autopct='%1.1f%%', startangle=140, colors=['#ff9999', '#66b3ff', '#99ff99'])
        plt.title('Skills Distribution in Resume')
        plt.axis('equal')
        plt.tight_layout()
        plt.savefig(img, format='png')
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode('utf8')

        # Determine areas for improvement
        areas_to_improve = [category for category, count in skill_count.items() if count == 0]

        # Save the analysis to MongoDB
        try:
            resumes_collection.insert_one({
                "filename": filename,
                "skills": skill_count,
                "score": total_score,
                "improvements": areas_to_improve
            })
        except Exception as e:
            return jsonify({"error": f"Error saving to database: {str(e)}"}), 500

        return jsonify({
            "message": "File successfully uploaded and analyzed",
            "file": filename,
            "score": total_score,
            "skill_count": skill_count,
            "plot_url": plot_url,
            "areas_to_improve": areas_to_improve
        })
    else:
        return jsonify({"error": "Invalid file format. Only PDF, DOCX, and TXT files are allowed."}), 400

if __name__ == "__main__":
    app.run(debug=True)
