
import streamlit as st
import pandas as pd

from resume_parser import parse_resume_file, extract_skills
from ranking import rank_candidates
from utils import parse_comma_separated

st.set_page_config(
    page_title="Resume Parsing and Candidate Ranking for Recruiters",
    layout="wide"
)

st.title("📄 Resume Parsing & Ranking System")

st.markdown(
    """
    - Upload resumes (PDF / DOCX / TXT)
    - Enter job description 
    - Get a **ranked list of candidates** with scores
    - Visualize score distribution
    """
)

st.sidebar.header("Configuration")
show_parsed_sections = st.sidebar.checkbox("Show parsed details per candidate", value=True)
show_raw_text = st.sidebar.checkbox("Show raw resume text (truncated)", value=False)
min_score = st.sidebar.slider("Minimum score to display", 0.0, 1.0, 0.0, 0.01)

def update_required_skills():
    extracted = extract_skills(st.session_state.job_description)
    st.session_state.required_skills = ", ".join(extracted) if extracted else ""

col1, col2 = st.columns(2)

with col1:
    st.header("1️⃣ Job Description & Criteria")

    job_description = st.text_area(
        "Paste the job description here",
        height=180,
        placeholder="Paste the full job description from your JD...",
        key="job_description",
        on_change=update_required_skills
    )

    required_skills_str = st.text_area(
        "Required skills (comma-separated)",
        help="Auto-extracted from job description. Edit as needed. E.g. Python, NLP, scikit-learn, REST APIs",
        key="required_skills"
    )

with col2:
    st.header("2️⃣ Upload Resumes")

    uploaded_files = st.file_uploader(
        "Upload one or more candidate resumes",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True,
        help="Supported formats: PDF, DOCX, TXT"
    )

job_keywords = []  # No manual keywords input
required_skills = parse_comma_separated(required_skills_str) if required_skills_str.strip() else parse_comma_separated(st.session_state.get('required_skills', ''))

st.markdown("---")

st.markdown("""
""", unsafe_allow_html=True)

if st.button("🚀 Run Parsing & Ranking", use_container_width=True):
        if not job_description.strip() and not uploaded_files:
            st.error("Please provide a job description and upload at least one resume.")
        elif not job_description.strip():
            st.error("Please provide a job description.")
        elif not uploaded_files:
            st.error("Please upload at least one resume.")
        else:
            st.header("3️⃣ Parse & Rank Candidates")
            with st.spinner("Parsing resumes and ranking candidates..."):
                candidates = []
                for f in uploaded_files:
                    parsed = parse_resume_file(f)
                    candidates.append(parsed)

                ranking_df = rank_candidates(
                    candidates=candidates,
                    job_description=job_description,
                    job_keywords=job_keywords,
                    required_skills=required_skills
                )

                ranking_df_filtered = ranking_df[ranking_df["Total Score"] >= min_score].reset_index(drop=True)
                ranking_df_filtered.index = ranking_df_filtered.index + 1

                st.subheader("🏆 Candidate Ranking")
                st.caption("Higher score indicates a better match to the job description and required skills.")

                st.dataframe(ranking_df_filtered, use_container_width=True)

                csv = ranking_df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "⬇️ Download full ranking as CSV",
                    data=csv,
                    file_name="candidate_ranking.csv",
                    mime="text/csv"
                )

                st.markdown("---")
                st.header("4️⃣ Visualizations")

                st.subheader("Score Distribution")
                chart_df = ranking_df.set_index("File Name")[["Total Score"]]
                st.bar_chart(chart_df)

                if show_parsed_sections or show_raw_text:
                    st.markdown("---")
                    st.header("5️⃣ Candidate Details")

                    # Create a mapping from file_name to candidate for ordering
                    candidate_map = {c.get("file_name"): c for c in candidates}

                    # Order candidates according to ranking
                    ordered_candidates = [candidate_map[file_name] for file_name in ranking_df_filtered["File Name"]]

                    for c in ordered_candidates:
                        row = ranking_df_filtered.loc[ranking_df_filtered["File Name"] == c.get("file_name")]
                        rank = row.index[0]
                        st.markdown(f"### Rank {rank}. 👤 {c.get('name') or c.get('file_name')}")
                        st.write(f"**Email:** {c.get('email') or 'N/A'}")
                        st.write(f"**Phone:** {c.get('phone') or 'N/A'}")

                        # Highlight matching skills in green
                        candidate_skills = c.get('skills', [])
                        if candidate_skills:
                            skill_parts = []
                            for skill in candidate_skills:
                                if skill.lower() in [s.lower() for s in required_skills]:
                                    skill_parts.append(f'<span style="color: #00FF00;">{skill}</span>')
                                else:
                                    skill_parts.append(skill)
                            skills_display = ', '.join(skill_parts)
                            st.markdown(f"**Skills:** {skills_display}", unsafe_allow_html=True)
                        else:
                            st.write("**Skills:** N/A")

                        if show_parsed_sections:
                            with st.expander("Education"):
                                st.write(c.get("education") or "Not detected")
                            with st.expander("Work Experience"):
                                st.write(c.get("experience") or "Not detected")

                        if show_raw_text:
                            with st.expander("Raw Resume Text (truncated)"):
                                text = c.get("raw_text") or ""
                                st.text(text[:2000] + ("..." if len(text) > 2000 else ""))

                st.success("Done! Candidates have been parsed and ranked.")
