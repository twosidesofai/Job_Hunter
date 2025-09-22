"""
Cover letter builder agent that generates personalized cover letters using OpenAI agent structure.
"""
import json
from typing import Dict, Any, Optional
from base_agent import BaseAgent, AgentResponse
from models import JobPosting, MasterResume, CoverLetter

class CoverLetterBuilderAgent(BaseAgent):
    """
    Agent responsible for generating personalized cover letters based on job postings and resume data.
    Uses OpenAI to create compelling, tailored cover letters.
    """
    
    def __init__(self):
        system_prompt = """
        You are a professional cover letter writing expert. Your role is to:
        
        1. Analyze job postings to understand company culture, role requirements, and key qualifications
        2. Review candidate profiles and identify the most compelling experiences and achievements
        3. Create personalized, engaging cover letters that connect candidate experience to job requirements
        4. Write in a professional yet personable tone that shows genuine interest
        5. Structure cover letters with strong opening, compelling body, and clear call-to-action
        
        When writing cover letters:
        - Open with a hook that shows knowledge of the company/role
        - Connect specific experiences to job requirements with concrete examples
        - Show enthusiasm for the company and role specifically
        - Quantify achievements where possible
        - Maintain professional tone while showing personality
        - Keep length appropriate (3-4 paragraphs, under 400 words)
        - End with a strong call-to-action
        
        Always create authentic, compelling content that helps the candidate stand out.
        """
        super().__init__("CoverLetterBuilder", system_prompt)
        self.supported_functions = ["analyze_company_culture", "match_experience_to_role", "write_cover_letter"]
    
    def execute_function(self, function_name: str, args: Dict[str, Any]) -> Any:
        """Execute specific cover letter building functions."""
        if function_name == "analyze_company_culture":
            return self._analyze_company_culture(args.get("job_posting", {}))
        elif function_name == "match_experience_to_role":
            return self._match_experience_to_role(args.get("resume", {}), args.get("job_posting", {}))
        elif function_name == "write_cover_letter":
            return self._write_cover_letter_content(args.get("job_posting", {}), args.get("resume", {}))
        else:
            raise ValueError(f"Unknown function: {function_name}")
    
    def process_request(self, request: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Process cover letter building requests."""
        try:
            if "build_cover_letter" in request.lower():
                job_posting = JobPosting(**context["job_posting"]) if context and "job_posting" in context else None
                master_resume = MasterResume(**context["master_resume"]) if context and "master_resume" in context else None
                
                if job_posting and master_resume:
                    cover_letter = self.build_cover_letter(job_posting, master_resume)
                    return AgentResponse(
                        success=True,
                        data={"cover_letter": cover_letter.model_dump()},
                        message="Successfully generated personalized cover letter"
                    )
                else:
                    return AgentResponse(
                        success=False,
                        message="Job posting and master resume data are required",
                        errors=["Missing required context data"]
                    )
            else:
                # Use OpenAI for general cover letter tasks
                messages = self._prepare_messages(request, context)
                response = self._make_openai_request(messages)
                return self._handle_response(response)
                
        except Exception as e:
            self.logger.error(f"Error processing cover letter request: {str(e)}")
            return AgentResponse(
                success=False,
                message="Failed to process cover letter building request",
                errors=[str(e)]
            )
    
    def build_cover_letter(self, job_posting: JobPosting, master_resume: MasterResume) -> CoverLetter:
        """
        Build a personalized cover letter for a specific job posting.
        
        Args:
            job_posting: The job posting to create cover letter for
            master_resume: The master resume containing candidate information
            
        Returns:
            CoverLetter with personalized content
        """
        try:
            # Generate the cover letter content using OpenAI
            cover_letter_content = self._generate_cover_letter_with_ai(job_posting, master_resume)
            
            # Extract key points highlighted in the cover letter
            key_points = self._extract_key_points(cover_letter_content, job_posting, master_resume)
            
            cover_letter = CoverLetter(
                job_posting_id=job_posting.id or f"{job_posting.company}_{job_posting.title}",
                content=cover_letter_content,
                key_points=key_points
            )
            
            return cover_letter
            
        except Exception as e:
            self.logger.error(f"Error building cover letter: {str(e)}")
            raise
    
    def _generate_cover_letter_with_ai(self, job_posting: JobPosting, master_resume: MasterResume) -> str:
        """
        Generate personalized cover letter content using OpenAI.
        """
        try:
            # Prepare context information
            resume_summary = self._create_resume_summary(master_resume)
            
            prompt = f"""
            Write a personalized cover letter for this job application:
            
            JOB POSTING:
            Company: {job_posting.company}
            Title: {job_posting.title}
            Location: {job_posting.location}
            Description: {job_posting.description}
            Requirements: {job_posting.requirements}
            
            CANDIDATE INFORMATION:
            Personal Info: {master_resume.personal_info}
            Professional Summary: {master_resume.summary}
            Key Experience: {resume_summary}
            
            INSTRUCTIONS:
            - Write a compelling 3-4 paragraph cover letter
            - Start with an engaging opening that shows knowledge of the company/role
            - Connect specific candidate experiences to job requirements
            - Show genuine enthusiasm for the opportunity
            - Include 1-2 specific examples with quantifiable achievements
            - End with a strong call-to-action
            - Keep it under 400 words
            - Use professional but personable tone
            - Do not include placeholder text or brackets
            
            Format as a complete, ready-to-send cover letter.
            """
            
            messages = self._prepare_messages(prompt)
            response = self._make_openai_request(messages)
            
            if response["choices"][0]["message"]["content"]:
                content = response["choices"][0]["message"]["content"].strip()
                
                # Post-process the content to ensure quality
                content = self._post_process_cover_letter(content, job_posting, master_resume)
                
                return content
            
        except Exception as e:
            self.logger.error(f"Error generating cover letter with AI: {str(e)}")
            return self._generate_fallback_cover_letter(job_posting, master_resume)
    
    def _create_resume_summary(self, master_resume: MasterResume) -> str:
        """
        Create a concise summary of key resume points for context.
        """
        summary_parts = []
        
        # Add top 2-3 experiences
        for i, exp in enumerate(master_resume.experience[:3]):
            summary_parts.append(f"- {exp.title} at {exp.company}: {exp.description[:100]}...")
        
        # Add key skills
        all_skills = []
        for skill_list in master_resume.skills.values():
            all_skills.extend(skill_list)
        
        if all_skills:
            summary_parts.append(f"- Key Skills: {', '.join(all_skills[:8])}")
        
        return "\n".join(summary_parts)
    
    def _post_process_cover_letter(self, content: str, job_posting: JobPosting, master_resume: MasterResume) -> str:
        """
        Post-process the cover letter to ensure quality and personalization.
        """
        # Ensure proper addressing
        if not content.startswith("Dear"):
            hiring_manager = "Hiring Manager"
            content = f"Dear {hiring_manager},\n\n{content}"
        
        # Ensure proper closing
        if not any(closing in content.lower() for closing in ["sincerely", "best regards", "thank you"]):
            content += f"\n\nSincerely,\n{master_resume.personal_info.get('name', 'Your Name')}"
        
        # Replace any remaining placeholders
        content = content.replace("[Company Name]", job_posting.company)
        content = content.replace("[Position]", job_posting.title)
        content = content.replace("[Your Name]", master_resume.personal_info.get('name', 'Your Name'))
        
        return content
    
    def _extract_key_points(self, cover_letter_content: str, job_posting: JobPosting, master_resume: MasterResume) -> list[str]:
        """
        Extract key points highlighted in the cover letter.
        """
        try:
            prompt = f"""
            Extract the key points/selling points mentioned in this cover letter:
            
            Cover Letter:
            {cover_letter_content}
            
            Please return a JSON array of 3-5 key points that this cover letter emphasizes about the candidate.
            Focus on:
            - Specific experiences mentioned
            - Skills highlighted
            - Achievements cited
            - Value propositions made
            
            Return only a JSON array of strings.
            """
            
            messages = self._prepare_messages(prompt)
            response = self._make_openai_request(messages)
            
            if response["choices"][0]["message"]["content"]:
                content = response["choices"][0]["message"]["content"]
                
                try:
                    # Find JSON array in the response
                    start = content.find("[")
                    end = content.rfind("]") + 1
                    json_str = content[start:end]
                    key_points = json.loads(json_str)
                    
                    return key_points if isinstance(key_points, list) else []
                    
                except json.JSONDecodeError:
                    # Fallback: extract points manually
                    return self._extract_key_points_fallback(cover_letter_content)
            
        except Exception as e:
            self.logger.error(f"Error extracting key points: {str(e)}")
            return self._extract_key_points_fallback(cover_letter_content)
    
    def _extract_key_points_fallback(self, cover_letter_content: str) -> list[str]:
        """
        Fallback method to extract key points from cover letter.
        """
        # Simple extraction based on common patterns
        key_points = []
        
        # Look for experience mentions
        if "years of experience" in cover_letter_content.lower():
            key_points.append("Relevant professional experience")
        
        # Look for achievement mentions
        if any(word in cover_letter_content.lower() for word in ["increased", "improved", "reduced", "achieved"]):
            key_points.append("Demonstrated track record of achievements")
        
        # Look for skill mentions
        if any(word in cover_letter_content.lower() for word in ["skilled", "expertise", "proficient"]):
            key_points.append("Strong technical and professional skills")
        
        # Look for leadership/team mentions
        if any(word in cover_letter_content.lower() for word in ["led", "managed", "team", "leadership"]):
            key_points.append("Leadership and team collaboration experience")
        
        return key_points if key_points else ["Relevant experience", "Strong skill set", "Enthusiasm for role"]
    
    def _generate_fallback_cover_letter(self, job_posting: JobPosting, master_resume: MasterResume) -> str:
        """
        Generate a basic cover letter when AI generation fails.
        """
        name = master_resume.personal_info.get("name", "Your Name")
        
        return f"""Dear Hiring Manager,

I am writing to express my strong interest in the {job_posting.title} position at {job_posting.company}. With my background in {master_resume.summary}, I am excited about the opportunity to contribute to your team.

In my previous roles, I have developed expertise that aligns well with your requirements. My experience includes {master_resume.experience[0].description if master_resume.experience else 'relevant professional experience'}. I am particularly drawn to this opportunity because of {job_posting.company}'s reputation and the role's focus on {job_posting.title.lower()}.

I am confident that my skills and enthusiasm would make me a valuable addition to your team. I would welcome the opportunity to discuss how I can contribute to {job_posting.company}'s continued success.

Thank you for your consideration. I look forward to hearing from you.

Sincerely,
{name}"""
    
    def _analyze_company_culture(self, job_posting: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze company culture from job posting."""
        # This would analyze the job posting for cultural indicators
        return {
            "values": [],
            "work_style": "collaborative",
            "company_size": "unknown"
        }
    
    def _match_experience_to_role(self, resume: Dict[str, Any], job_posting: Dict[str, Any]) -> Dict[str, Any]:
        """Match candidate experience to role requirements."""
        # This would find the best experience matches
        return {
            "matching_experiences": [],
            "relevant_skills": [],
            "achievement_examples": []
        }
    
    def _write_cover_letter_content(self, job_posting: Dict[str, Any], resume: Dict[str, Any]) -> str:
        """Write cover letter content."""
        # This would be called by the function calling mechanism
        return "Cover letter content would be generated here."