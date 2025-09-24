from cover_letter_builder import CoverLetterBuilderAgent

class DummyCoverLetterBuilderAgent(CoverLetterBuilderAgent):
    def build_cover_letter(self, job, resume):
        return f"Cover letter for {job['title']}"
    def generate_cover_letter(self, job, resume):
        return self.build_cover_letter(job, resume)

def test_generate_cover_letter():
    agent = DummyCoverLetterBuilderAgent()
    job = {"title": "AI Engineer", "description": "Work on AI projects."}
    resume = {"name": "John Doe", "skills": ["Python", "AI"]}
    letter = agent.generate_cover_letter(job, resume)
    assert isinstance(letter, str)
    assert "AI Engineer" in letter

