from typing import Dict, List
from agents.granite_client import safe_generate
import subprocess
import os


def _format_local_resume(master_profile: Dict, job: Dict, projects: List[Dict]) -> str:
    lines: List[str] = []
    lines.append(f"# Resume Target: {job.get('title')}")
    lines.append(f"Company: {job.get('company')}")
    lines.append("## Key Skills")
    lines.append(", ".join(sorted(set(master_profile.get("skills", [])))))
    if projects:
        lines.append("## Relevant Projects")
        for p in projects:
            desc = (p.get("description") or "")[:80]
            lines.append(f"- {p['name']}: {desc}")
    lines.append("## Experience (Action → Context → Result)")
    for exp in master_profile.get("experience", []):
        lines.append(f"- Action: {exp['action']}\n  Context: {exp['context']}\n  Result: {exp['result']}")
    return "\n".join(lines)


def build_granite_resume(master_profile: Dict, job: Dict, projects: List[Dict]) -> str:
    sr = open("samp_res.tex", "r", encoding="utf-8").read()
    prompt = f"""
You are an ATS optimization assistant and a skilled LaTeX resume writer. Generate a tailored resume using the sample_resume.tex template. 
OUTPUT A COMPLETE LaTeX document with this EXACT structure present in the sample below: {", ".join(sr.splitlines())}
Change the content to reflect the JOB DESCRIPTION and the CANDIDATE SKILLS and PROJECTS provided.
JOB TITLE: {job.get('title')}
COMPANY: {job.get('company')}
JOB DESCRIPTION:
{job.get('description','')[:1500]}
EXPERIENCE: {", ".join([f"Action: {exp['action']}, Context: {exp['context']}, Result: {exp['result']}" for exp in master_profile.get("experience", [])])}
CANDIDATE SKILLS: {', '.join(master_profile.get('skills', []))}
PROJECTS:
{'; '.join([p['name'] + ': ' + (p.get('description','')[:120]) for p in projects])}

Output COMPLETE LaTeX Code with sections:
1. Summary (2 sentences)
2. Core Skills (comma separated)
3. Achievements (Action → Context → Result bullets) (3-5 items)
Use only real candidate skills.

Ensure the LaTeX compiles without errors and conflicts.
"""
    generated = safe_generate(prompt)
    
    # If AI generation failed, use fallback
    if not generated:
        return _format_local_resume(master_profile, job, projects)
    
    # Post-process AI output to fix common issues
    # 1. Remove text before \documentclass
    if '\\documentclass' in generated:
        generated = '\\documentclass' + generated.split('\\documentclass', 1)[1]
    
    # 2. Replace XCharter font with basic font to avoid compatibility issues
    generated = generated.replace('\\usepackage{XCharter}', '% XCharter removed for compatibility')
    generated = generated.replace('\\usepackage[T1]{fontenc}', '')
    
    # 3. Close unclosed environments before \end{document}
    if '\\begin{itemize}' in generated and generated.count('\\begin{itemize}') > generated.count('\\end{itemize}'):
        # Add missing \end{itemize} before \end{document}
        if '\\end{document}' in generated:
            generated = generated.replace('\\end{document}', '\\end{itemize}\n\n\\end{document}')
        else:
            generated += '\n\\end{itemize}\n'
    
    # 4. Ensure document ends properly
    if '\\end{document}' not in generated:
        generated += '\n\n\\end{document}\n'
    
    # 5. Remove problematic placeholders
    generated = generated.replace('[Contact Info]', '')
    generated = generated.replace('[Candidate Name]', 'Professional')
    
    # Save generated content
    job_id = job.get('id', 'temp').replace('/', '_')
    tex_file = f'resume_{job_id}.tex'
    pdf_file = f'resume_{job_id}.pdf'
    
    try:
        # Save LaTeX source
        with open(tex_file, 'w', encoding='utf-8') as f:
            f.write(generated)
        print(f"[INFO] LaTeX saved to {tex_file}")
        
        # Generate PDF using system pdflatex
        try:
            result = subprocess.run(
                ['pdflatex', '-interaction=nonstopmode', tex_file],
                capture_output=True,
                timeout=30,
                cwd='.',
                text=True
            )
            if result.returncode == 0 and os.path.exists(pdf_file):
                print(f"[SUCCESS] PDF generated: {pdf_file}")
            else:
                print(f"[WARN] PDFLaTeX failed: {result.stderr[:200]}")
        except FileNotFoundError:
            print(f"[WARN] pdflatex not found in PATH")
        except Exception as pdf_err:
            print(f"[WARN] PDF generation failed: {pdf_err}")
            
    except Exception as e:
        print(f"[ERROR] Could not save resume: {e}")
    
    # Return the generated content
    return generated


def build_cheat_sheet(master_profile: Dict, job: Dict) -> Dict:
    return {
        "job_id": job.get("id"),
        "years_experience": master_profile.get("years_experience"),
        "primary_stack": ", ".join(master_profile.get("skills", [])[:5]),
        "work_auth": master_profile.get("work_auth"),
        "salary_expectation": master_profile.get("salary_expectation", "Negotiable"),
    }
