
# Resume Parsing and Candidate Ranking for Recruiters

This project is a fully functional **Streamlit** application that allows recruiters to:

- Upload multiple resumes (PDF / DOCX / TXT)
- Automatically **parse** key information from each resume:
  - Name
  - Contact Information (Email, Phone)
  - Education
  - Work Experience (heuristic)
  - Skills (heuristic)
- Enter a **job description**, **keywords**, and **required skills**
- Automatically **rank candidates** using:
  - TF-IDF similarity between resume text and job description
  - Keyword match (presence of JD keywords in resumes)
  - Required skill match
- Visualize:
  - Candidate score distribution
  - Skill coverage across candidates

## Technologies Used

- Python
- Streamlit
- pdfminer.six
- python-docx
- Pandas
- Scikit-learn

## Run locally

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud

1. Push this folder to GitHub.
2. On Streamlit Community Cloud, create a new app and point it to `app.py`.
3. It will auto-install from `requirements.txt` and run.
