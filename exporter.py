# exporter.py
"""
Exports resumes and cover letters to Word/PDF format in the Applications folder.
"""


import os
from abc import ABC, abstractmethod
from typing import Dict
from docx import Document
from fpdf import FPDF

# Abstract base agent for exporting
class ExporterAgent(ABC):
	@abstractmethod
	def export(self, resume: Dict, cover_letter: str, company: str, job_title: str, folder: str = "Applications"):
		pass

# DOCX and PDF exporter agent
class DocxPdfExporterAgent(ExporterAgent):
	def export(self, resume: Dict, cover_letter: str, company: str, job_title: str, folder: str = "Applications"):
		safe_company = company.replace(" ", "_")
		safe_title = job_title.replace(" ", "_")
		app_dir = os.path.join(folder, f"{safe_company}_{safe_title}")
		os.makedirs(app_dir, exist_ok=True)

		# Export resume to DOCX
		resume_docx_path = os.path.join(app_dir, "resume.docx")
		self._export_resume_docx(resume, resume_docx_path)

		# Export cover letter to DOCX
		cover_docx_path = os.path.join(app_dir, "cover_letter.docx")
		self._export_cover_letter_docx(cover_letter, cover_docx_path)

		# Export resume to PDF
		resume_pdf_path = os.path.join(app_dir, "resume.pdf")
		self._export_text_pdf(self._resume_text(resume), resume_pdf_path)

		# Export cover letter to PDF
		cover_pdf_path = os.path.join(app_dir, "cover_letter.pdf")
		self._export_text_pdf(cover_letter, cover_pdf_path)

	def _export_resume_docx(self, resume: Dict, path: str):
		doc = Document()
		doc.add_heading(resume.get('name', ''), 0)
		contact = resume.get('contact', {})
		doc.add_paragraph(f"Email: {contact.get('email', '')} | Phone: {contact.get('phone', '')} | Location: {contact.get('location', '')}")
		doc.add_paragraph(resume.get('summary', ''))
		doc.add_heading('Experience', level=1)
		for exp in resume.get('experience', []):
			doc.add_paragraph(f"{exp.get('title', '')} at {exp.get('company', '')}", style='List Bullet')
			doc.add_paragraph(exp.get('description', ''))
		doc.add_heading('Education', level=1)
		for edu in resume.get('education', []):
			doc.add_paragraph(f"{edu.get('degree', '')}, {edu.get('school', '')} ({edu.get('year', '')})", style='List Bullet')
		doc.add_heading('Skills', level=1)
		doc.add_paragraph(", ".join(resume.get('skills', [])))
		doc.save(path)

	def _export_cover_letter_docx(self, cover_letter: str, path: str):
		doc = Document()
		for line in cover_letter.split('\n'):
			doc.add_paragraph(line)
		doc.save(path)

	def _export_text_pdf(self, text: str, path: str):
		pdf = FPDF()
		pdf.add_page()
		pdf.set_auto_page_break(auto=True, margin=15)
		pdf.set_font("Arial", size=12)
		for line in text.split('\n'):
			pdf.cell(0, 10, txt=line, ln=1)
		pdf.output(path)

	def _resume_text(self, resume: Dict) -> str:
		lines = [resume.get('name', '')]
		contact = resume.get('contact', {})
		lines.append(f"Email: {contact.get('email', '')} | Phone: {contact.get('phone', '')} | Location: {contact.get('location', '')}")
		lines.append(resume.get('summary', ''))
		lines.append('Experience:')
		for exp in resume.get('experience', []):
			lines.append(f"- {exp.get('title', '')} at {exp.get('company', '')}: {exp.get('description', '')}")
		lines.append('Education:')
		for edu in resume.get('education', []):
			lines.append(f"- {edu.get('degree', '')}, {edu.get('school', '')} ({edu.get('year', '')})")
		lines.append('Skills:')
		lines.append(", ".join(resume.get('skills', [])))
		return '\n'.join(lines)

# Example usage (for testing)
if __name__ == "__main__":
	resume = {
		"name": "John Doe",
		"contact": {"email": "john.doe@email.com", "phone": "123-456-7890", "location": "Remote, USA"},
		"summary": "Experienced software engineer with a focus on Python and distributed systems.",
		"experience": [
			{"title": "Software Engineer", "company": "TechCorp", "description": "Developed scalable backend services in Python."}
		],
		"education": [
			{"degree": "B.Sc. Computer Science", "school": "State University", "year": "2016"}
		],
		"skills": ["Python", "Distributed Systems", "APIs"]
	}
	cover_letter = "Dear TechCorp,\nI am excited to apply.\nSincerely, John Doe"
	agent = DocxPdfExporterAgent()
	agent.export(resume, cover_letter, "TechCorp", "Software Engineer")
