"""
Resume builder agent that generates tailored resumes using OpenAI agent structure.
"""
import json
from typing import List, Dict, Any, Optional
from base_agent import BaseAgent, AgentResponse
from models import JobPosting, MasterResume, TailoredResume, ExperienceItem

class ResumeBuilderAgent(BaseAgent):
    """
    Agent responsible for generating tailored resumes based on job postings and master resume data.
    Uses OpenAI to intelligently select and customize resume content.
    """
    
    def __init__(self):
        system_prompt = """
        You are a professional resume optimization agent. Your role is to:
        
        1. Analyze job postings and identify key requirements, skills, and qualifications
        2. Review a master resume and select the most relevant experiences and skills
        3. Tailor resume content to match job requirements while maintaining authenticity
        4. Optimize resume summaries, experience descriptions, and skill listings
        5. Ensure ATS (Applicant Tracking System) compatibility
        
        When building tailored resumes:
        - Prioritize experiences that directly relate to the job requirements
        - Use keywords from the job posting naturally in descriptions
        - Quantify achievements with specific metrics when possible
        - Keep content concise but impactful
        - Maintain chronological order and professional formatting
        - Highlight transferable skills for career changes
        
        Always return structured JSON data that matches the TailoredResume model schema.
        """
        super().__init__("ResumeBuilder", system_prompt)
        self.supported_functions = ["analyze_job_requirements", "select_relevant_experience", "optimize_resume_content"]
    
    def execute_function(self, function_name: str, args: Dict[str, Any]) -> Any:
        """Execute specific resume building functions."""
        if function_name == "analyze_job_requirements":
            return self._analyze_job_requirements(args.get("job_posting", {}))
        elif function_name == "select_relevant_experience":
            return self._select_relevant_experience(args.get("master_resume", {}), args.get("job_requirements", {}))
        elif function_name == "optimize_resume_content":
            return self._optimize_resume_content(args.get("resume_content", {}), args.get("job_posting", {}))
        else:
            raise ValueError(f"Unknown function: {function_name}")
    
    def process_request(self, request: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Process resume building requests."""
        try:
            if "build_resume" in request.lower():
                job_posting = JobPosting(**context["job_posting"]) if context and "job_posting" in context else None
                master_resume = MasterResume(**context["master_resume"]) if context and "master_resume" in context else None
                
                if job_posting and master_resume:
                    tailored_resume = self.build_tailored_resume(job_posting, master_resume)
                    return AgentResponse(
                        success=True,
                        data={"tailored_resume": tailored_resume.model_dump()},
                        message="Successfully generated tailored resume"
                    )
                else:
                    return AgentResponse(
                        success=False,
                        message="Job posting and master resume data are required",
                        errors=["Missing required context data"]
                    )
            else:
                # Use OpenAI for general resume optimization tasks
                messages = self._prepare_messages(request, context)
                response = self._make_openai_request(messages)
                return self._handle_response(response)
                
        except Exception as e:
            self.logger.error(f"Error processing resume request: {str(e)}")
            return AgentResponse(
                success=False,
                message="Failed to process resume building request",
                errors=[str(e)]
            )
    
    def build_tailored_resume(self, job_posting: JobPosting, master_resume: MasterResume) -> TailoredResume:
        """
        Build a tailored resume for a specific job posting.
        
        Args:
            job_posting: The job posting to tailor the resume for
            master_resume: The master resume containing all experience and skills
            
        Returns:
            TailoredResume optimized for the job posting
        """
        try:
            # Step 1: Analyze job requirements using OpenAI
            job_requirements = self._analyze_job_requirements_with_ai(job_posting)
            
            # Step 2: Select and tailor experience
            tailored_experience = self._select_and_tailor_experience(master_resume, job_requirements)
            
            # Step 3: Create tailored summary
            tailored_summary = self._create_tailored_summary(master_resume.summary, job_requirements)
            
            # Step 4: Select relevant skills
            relevant_skills = self._select_relevant_skills(master_resume.skills, job_requirements)
            
            # Step 5: Select relevant projects and certifications
            relevant_projects = self._select_relevant_projects(master_resume.projects, job_requirements)
            relevant_certifications = self._select_relevant_certifications(master_resume.certifications, job_requirements)
            
            tailored_resume = TailoredResume(
                job_posting_id=job_posting.id or f"{job_posting.company}_{job_posting.title}",
                personal_info=master_resume.personal_info,
                summary=tailored_summary,
                experience=tailored_experience,
                education=master_resume.education,
                skills=relevant_skills,
                certifications=relevant_certifications,
                projects=relevant_projects
            )
            
            return tailored_resume
            
        except Exception as e:
            self.logger.error(f"Error building tailored resume: {str(e)}")
            raise
    
    def _analyze_job_requirements_with_ai(self, job_posting: JobPosting) -> Dict[str, Any]:
        """
        Analyze job posting to extract key requirements using OpenAI.
        """
        try:
            prompt = f"""
            Analyze this job posting and extract key requirements:
            
            Job Title: {job_posting.title}
            Company: {job_posting.company}
            Description: {job_posting.description}
            Requirements: {job_posting.requirements}
            
            Please extract and return a JSON object with:
            - required_skills: List of technical skills mentioned
            - preferred_skills: List of nice-to-have skills
            - experience_level: Required years of experience
            - key_responsibilities: Main job responsibilities
            - industry_keywords: Important industry/domain terms
            - soft_skills: Mentioned soft skills and qualities
            - education_requirements: Educational requirements if any
            
            Focus on actionable requirements that should influence resume content.
            """
            
            messages = self._prepare_messages(prompt)
            response = self._make_openai_request(messages)
            
            if response["choices"][0]["message"]["content"]:
                content = response["choices"][0]["message"]["content"]
                
                # Extract JSON from the response
                try:
                    start = content.find("{")
                    end = content.rfind("}") + 1
                    json_str = content[start:end]
                    requirements = json.loads(json_str)
                    return requirements
                except json.JSONDecodeError as e:
                    self.logger.error(f"Error parsing job requirements JSON: {str(e)}")
                    return self._fallback_job_analysis(job_posting)
            
        except Exception as e:
            self.logger.error(f"Error analyzing job requirements: {str(e)}")
            return self._fallback_job_analysis(job_posting)
    
    def _select_and_tailor_experience(self, master_resume: MasterResume, job_requirements: Dict[str, Any]) -> List[ExperienceItem]:
        """
        Select and tailor experience items based on job requirements.
        """
        try:
            # Use OpenAI to select and tailor experience
            prompt = f"""
            Given this master resume experience and job requirements, select and tailor the most relevant experience items.
            
            Master Resume Experience:
            {json.dumps([exp.model_dump() for exp in master_resume.experience], indent=2)}
            
            Job Requirements:
            {json.dumps(job_requirements, indent=2)}
            
            Please:
            1. Select the most relevant experience items (limit to 3-4 most relevant)
            2. Tailor the descriptions to highlight skills mentioned in job requirements
            3. Add relevant keywords naturally
            4. Quantify achievements where possible
            5. Focus on accomplishments that match the job needs
            
            Return a JSON array of experience items with the same structure as the input.
            """
            
            messages = self._prepare_messages(prompt)
            response = self._make_openai_request(messages)
            
            if response["choices"][0]["message"]["content"]:
                content = response["choices"][0]["message"]["content"]
                
                try:
                    start = content.find("[")
                    end = content.rfind("]") + 1
                    json_str = content[start:end]
                    experience_data = json.loads(json_str)
                    
                    tailored_experience = []
                    for exp_data in experience_data:
                        exp_item = ExperienceItem(**exp_data)
                        tailored_experience.append(exp_item)
                    
                    return tailored_experience
                    
                except (json.JSONDecodeError, ValueError) as e:
                    self.logger.error(f"Error parsing tailored experience JSON: {str(e)}")
                    # Fallback: return top 3 experiences from master resume
                    return master_resume.experience[:3]
            
        except Exception as e:
            self.logger.error(f"Error selecting and tailoring experience: {str(e)}")
            return master_resume.experience[:3]
    
    def _create_tailored_summary(self, master_summary: str, job_requirements: Dict[str, Any]) -> str:
        """
        Create a tailored professional summary.
        """
        try:
            prompt = f"""
            Tailor this professional summary for the job requirements:
            
            Original Summary: {master_summary}
            
            Job Requirements:
            {json.dumps(job_requirements, indent=2)}
            
            Please rewrite the summary to:
            1. Highlight skills and experience relevant to the job
            2. Include key industry terms and requirements
            3. Keep it concise (2-3 sentences)
            4. Make it compelling and ATS-friendly
            5. Maintain authenticity
            
            Return only the tailored summary text.
            """
            
            messages = self._prepare_messages(prompt)
            response = self._make_openai_request(messages)
            
            if response["choices"][0]["message"]["content"]:
                return response["choices"][0]["message"]["content"].strip()
            
        except Exception as e:
            self.logger.error(f"Error creating tailored summary: {str(e)}")
            
        # Fallback to original summary
        return master_summary
    
    def _select_relevant_skills(self, master_skills: Dict[str, List[str]], job_requirements: Dict[str, Any]) -> List[str]:
        """
        Select the most relevant skills for the job.
        """
        try:
            required_skills = job_requirements.get("required_skills", [])
            preferred_skills = job_requirements.get("preferred_skills", [])
            all_job_skills = required_skills + preferred_skills
            
            # Flatten master skills
            all_master_skills = []
            for category, skills in master_skills.items():
                all_master_skills.extend(skills)
            
            # Find matching skills (case-insensitive)
            relevant_skills = []
            job_skills_lower = [skill.lower() for skill in all_job_skills]
            
            for skill in all_master_skills:
                if any(job_skill in skill.lower() or skill.lower() in job_skill for job_skill in job_skills_lower):
                    relevant_skills.append(skill)
            
            # Add some general skills if we don't have enough matches
            if len(relevant_skills) < 8:
                for category, skills in master_skills.items():
                    for skill in skills:
                        if skill not in relevant_skills and len(relevant_skills) < 12:
                            relevant_skills.append(skill)
            
            return relevant_skills[:12]  # Limit to top 12 skills
            
        except Exception as e:
            self.logger.error(f"Error selecting relevant skills: {str(e)}")
            # Fallback: return first 12 skills from master resume
            all_skills = []
            for skills_list in master_skills.values():
                all_skills.extend(skills_list)
            return all_skills[:12]
    
    def _select_relevant_projects(self, master_projects: List[Dict[str, str]], job_requirements: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Select the most relevant projects for the job.
        """
        # Simple relevance scoring based on keyword matching
        relevant_projects = []
        required_skills = job_requirements.get("required_skills", [])
        keywords = job_requirements.get("industry_keywords", [])
        
        for project in master_projects:
            score = 0
            project_text = f"{project.get('name', '')} {project.get('description', '')}".lower()
            
            for skill in required_skills:
                if skill.lower() in project_text:
                    score += 2
            
            for keyword in keywords:
                if keyword.lower() in project_text:
                    score += 1
            
            if score > 0:
                relevant_projects.append((score, project))
        
        # Sort by relevance score and return top 3
        relevant_projects.sort(key=lambda x: x[0], reverse=True)
        return [project[1] for project in relevant_projects[:3]]
    
    def _select_relevant_certifications(self, master_certifications: List[str], job_requirements: Dict[str, Any]) -> List[str]:
        """
        Select the most relevant certifications for the job.
        """
        relevant_certs = []
        required_skills = job_requirements.get("required_skills", [])
        industry_keywords = job_requirements.get("industry_keywords", [])
        
        for cert in master_certifications:
            cert_lower = cert.lower()
            
            # Check if certification relates to job requirements
            for skill in required_skills:
                if skill.lower() in cert_lower:
                    relevant_certs.append(cert)
                    break
            
            for keyword in industry_keywords:
                if keyword.lower() in cert_lower:
                    if cert not in relevant_certs:
                        relevant_certs.append(cert)
                    break
        
        # If no matches, include all certifications
        return relevant_certs if relevant_certs else master_certifications
    
    def _analyze_job_requirements(self, job_posting: Dict[str, Any]) -> Dict[str, Any]:
        """Basic fallback job requirements analysis."""
        return {
            "required_skills": [],
            "preferred_skills": [],
            "experience_level": "3+ years",
            "key_responsibilities": [],
            "industry_keywords": [],
            "soft_skills": [],
            "education_requirements": []
        }
    
    def _fallback_job_analysis(self, job_posting: JobPosting) -> Dict[str, Any]:
        """Fallback job analysis when AI analysis fails."""
        # Basic keyword extraction
        description_lower = f"{job_posting.description} {job_posting.requirements}".lower()
        
        common_skills = [
            "python", "java", "javascript", "react", "node.js", "sql", "aws", "docker", 
            "kubernetes", "git", "linux", "html", "css", "mongodb", "postgresql"
        ]
        
        found_skills = [skill for skill in common_skills if skill in description_lower]
        
        return {
            "required_skills": found_skills,
            "preferred_skills": [],
            "experience_level": "3+ years",
            "key_responsibilities": [],
            "industry_keywords": [job_posting.company, job_posting.title.split()[0]],
            "soft_skills": ["communication", "teamwork", "problem-solving"],
            "education_requirements": []
        }