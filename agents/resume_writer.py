from typing import Dict, List
from agents.llm_client import safe_generate
import subprocess
import os
import shutil
from pathlib import Path


def _format_local_resume(master_profile: Dict, job: Dict, projects: List[Dict]) -> str:
    lines: List[str] = []
    lines.append(f"# Resume Target: {job.get('title')}")
    lines.append(f"Company: {job.get('company')}")
    lines.append(f"Name: {master_profile.get('name','')}")
    lines.append(f"Email: {master_profile.get('email','')}")
    lines.append(f"LinkedIn: {master_profile.get('linkedin','')}")
    lines.append(f"GitHub: https://github.com/{master_profile.get('github_username','')}")
    
    # Add summary section
    summary = master_profile.get('summary', '')
    if summary:
        lines.append(f"\n## Summary\n{summary}")
    
    lines.append("\n## Key Skills\n" + ", ".join(sorted(set(master_profile.get("skills", [])))))
    
    # Education section
    lines.append("\n## Education")
    for edu in master_profile.get("education", []):
        line = f"- {edu.get('degree','')} in {edu.get('field','')} at {edu.get('institution','')} ({edu.get('startDate','')}–{edu.get('endDate','')})"
        if edu.get('location'):
            line += f" | {edu['location']}"
        lines.append(line)
        if edu.get('gpa'):
            lines.append(f"  GPA: {edu['gpa']}")
    
    # Experience section
    lines.append("\n## Experience")
    for exp in master_profile.get("experience", []):
        lines.append(f"- **{exp.get('role','')}** at {exp.get('company','')} ({exp.get('date','')})")
        lines.append(f"  {exp.get('description','')}")
    
    # Projects section
    if projects:
        lines.append("\n## Relevant Projects")
        for p in projects:
            proj_name = p.get('Name', p.get('name', p.get('title', '')))
            lines.append(f"- **{proj_name}**")
            if p.get('Point1'):
                lines.append(f"  • {p['Point1']}")
            if p.get('Point2'):
                lines.append(f"  • {p['Point2']}")
    
    # Certifications section
    lines.append("\n## Certifications")
    certs = master_profile.get("certifications", [])
    if certs:
        for cert in certs:
            lines.append(f"- **{cert.get('name','')}** -- {cert.get('issuer','')} ({cert.get('date','')})")
            if cert.get('link'):
                lines.append(f"  Link: {cert['link']}")
    else:
        lines.append("- None")
    
    return "\n".join(lines)

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"
STATIC_DIR.mkdir(exist_ok=True)


def build_granite_resume(master_profile: Dict, job: Dict, projects: List[Dict], sanitized_job_id: str | None = None) -> str:
    sr = open("samp_res.tex", "r", encoding="utf-8").read()
    
    # Compose education lines
    edu_lines = []
    for edu in master_profile.get("education", []):
        line = f"{edu.get('degree','')} in {edu.get('field','')} at {edu.get('institution','')} ({edu.get('startDate','')}–{edu.get('endDate','')})"
        if edu.get('location'): 
            line += f" | {edu['location']}"
        if edu.get('gpa'): 
            line += f", GPA: {edu['gpa']}"
        edu_lines.append(line)
    
    # Compose certification lines
    cert_lines = []
    for cert in master_profile.get("certifications", []):
        cert_lines.append(f"{cert.get('name','')} ({cert.get('issuer','')}, {cert.get('date','')}) [{cert.get('link','')}]")
    
    # Experience lines
    exp_lines = []
    for exp in master_profile.get("experience", []):
        exp_lines.append(f"{exp.get('role','')} at {exp.get('company','')} ({exp.get('date','')}): {exp.get('description','')}")
    
    # Summary (no bio in this profile)
    summary = master_profile.get('summary', '')
    
    # Format projects for prompt
    project_lines = []
    for p in projects:
        proj_name = p.get('Name', p.get('name', p.get('title', '')))
        point1 = p.get('Point1', '')
        point2 = p.get('Point2', '')
        project_lines.append(f"{proj_name}: {point1} {point2}")
    
    # Achievements
    achievements = master_profile.get('achievements', [])
    
    prompt = f"""
You are an expert ATS-optimized LaTeX resume writer. Your task is to generate a tailored, professional resume in LaTeX format.

CRITICAL INSTRUCTIONS:
1. Use the provided SAMPLE TEMPLATE structure below as your EXACT formatting guide
2. Replace ONLY the content (names, details, descriptions) - keep ALL LaTeX formatting identical
3. DO NOT add the job description to the Experience section - Experience comes from CANDIDATE EXPERIENCE only
4. DO NOT invent information - use only data provided below
5. Ensure proper LaTeX syntax with correct newlines and spacing
6. Output ONLY valid LaTeX code that compiles without errors

=== SAMPLE TEMPLATE (DO NOT MODIFY STRUCTURE) ===
{sr}
=== END SAMPLE TEMPLATE ===

=== TARGET JOB (For tailoring language and keywords only) ===
Job Title: {job.get('title')}
Company: {job.get('company')}
Job Description: {job.get('description','')[:1500]}
=== END TARGET JOB ===

=== CANDIDATE INFORMATION (Use this data to fill the template) ===

CONTACT INFORMATION:
- Full Name: {master_profile.get('name','')}
- Email: {master_profile.get('email','')}
- LinkedIn: {master_profile.get('linkedin','')}
- GitHub: https://github.com/{master_profile.get('github_username','')}

PROFESSIONAL SUMMARY:
{summary}

TECHNICAL SKILLS:
{', '.join(master_profile.get('skills', []))}

EDUCATION (List ALL entries in chronological order):
{chr(10).join('- ' + line for line in edu_lines)}

WORK EXPERIENCE (Use ONLY these experiences - DO NOT use job description):
{chr(10).join('- ' + line for line in exp_lines)}

CERTIFICATIONS (List ALL entries with links):
{chr(10).join('- ' + line for line in cert_lines)}

ACHIEVEMENTS (List if provided):
{chr(10).join('- ' + achievement for achievement in achievements) if achievements else '- None provided'}

RELEVANT PROJECTS (Each has two bullet points):
{chr(10).join('- ' + line for line in project_lines)}

=== END CANDIDATE INFORMATION ===

REQUIRED OUTPUT STRUCTURE (in this exact order):
1. \\documentclass and preamble (copy from sample template)
2. Contact Information section (name, email, LinkedIn, GitHub)
3. Professional Summary (2-3 sentences, tailor to job keywords)
4. Core Skills section - Group as:
   - Languages: [programming languages only]
   - Tools & Technologies: [frameworks, databases, cloud platforms, tools]
   - Relevant Coursework: [if applicable]
5. Education section (all entries with degree, institution, location, dates, GPA if available)
6. Experience section (use ONLY candidate's work experience with role, company, date, and description)
7. Projects section (relevant projects with TWO bullet points each from Point1 and Point2)
8. Certifications section (all entries with name, issuer, date, and \\href link)
9. Achievements section (bullet points, ONLY if achievements are provided)
10. \\end{{document}}

FORMATTING REQUIREMENTS:
- Use proper LaTeX spacing: \\vspace{{3pt}}, \\hrule for section dividers
- Ensure all \\begin{{itemize}} have matching \\end{{itemize}}
- Use [leftmargin=1em, itemsep=0em, topsep=0em] for itemize environment
- Use \\textbf for emphasis, \\href for links
- Use \\textit for job titles/roles
- End with \\end{{document}}

CONTENT TAILORING:
- Incorporate relevant keywords from the job description naturally into the summary
- Emphasize skills that match the target role
- Use action verbs and quantifiable metrics from the experience and projects
- Keep language professional and concise

OUTPUT ONLY THE COMPLETE LATEX CODE - NO EXPLANATIONS OR MARKDOWN WRAPPERS.
"""
    
    generated = safe_generate(prompt)
    
    if not generated:
        return _format_local_resume(master_profile, job, projects)
    
    # Extract LaTeX code if wrapped in markdown
    if '\\documentclass' in generated:
        generated = '\\documentclass' + generated.split('\\documentclass', 1)[1]
    
    # Remove incompatible packages
    generated = generated.replace('\\usepackage{XCharter}', '% XCharter removed for compatibility')
    generated = generated.replace('\\usepackage[T1]{fontenc}', '')
    
    # Fix unmatched itemize blocks
    if '\\begin{itemize}' in generated and generated.count('\\begin{itemize}') > generated.count('\\end{itemize}'):
        if '\\end{document}' in generated:
            generated = generated.replace('\\end{document}', '\\end{itemize}\n\n\\end{document}')
        else:
            generated += '\n\\end{itemize}\n'
    
    # Ensure document ends properly
    if '\\end{document}' not in generated:
        generated += '\n\\end{document}\n'
    
    # Replace placeholders
    generated = generated.replace('[Contact Info]', '')
    generated = generated.replace('[Candidate Name]', master_profile.get('name','Professional'))
    
    # Determine sanitized job id if not provided
    if not sanitized_job_id:
        raw_id = str(job.get('id', 'resume'))
        sanitized_job_id = ''.join([c if str(c).isalnum() else '_' for c in raw_id])

    # Save files into static directory
    tex_file = STATIC_DIR / f'resume_{sanitized_job_id}.tex'
    pdf_file = STATIC_DIR / f'resume_{sanitized_job_id}.pdf'
    
    try:
        tex_file.write_text(generated, encoding='utf-8')
        print(f"[INFO] LaTeX saved to {tex_file}")

        # Compile with pdflatex into STATIC_DIR (Docker installs TeX Live)
        if shutil.which('pdflatex'):
            cmd = ['pdflatex', '-interaction=nonstopmode', f'-output-directory={STATIC_DIR}', str(tex_file)]
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=180,
                text=True
            )
            if result.returncode == 0 and pdf_file.exists():
                print(f"[SUCCESS] PDF generated via pdflatex: {pdf_file}")
            else:
                print(f"[WARN] PDFLaTeX failed: {result.stdout[:200]} {result.stderr[:200]}")
        else:
            print("[WARN] pdflatex not found; PDF will not be generated")
    except Exception as e:
        print(f"[ERROR] Could not save resume: {e}")
    
    return generated


def build_cheat_sheet(master_profile: Dict, job: Dict) -> Dict:
    return {
        "job_id": job.get("id"),
        "years_experience": master_profile.get("years_experience"),
        "primary_stack": ", ".join(master_profile.get("skills", [])[:5]),
        "work_auth": master_profile.get("work_auth"),
    }

def build_preview_markdown(master_profile: Dict, job: Dict, projects: List[Dict]) -> str:
    """Return a simple Markdown preview independent of LaTeX compile.
    Uses profile + job data so UI can render a readable preview.
    """
    return _format_local_resume(master_profile, job, projects)
