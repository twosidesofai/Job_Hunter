"""
Application tracker agent that manages job application data using OpenAI agent structure.
"""
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy import create_engine, Column, String, DateTime, Text, Boolean, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.dialects.postgresql import UUID
import uuid

from base_agent import BaseAgent, AgentResponse
from models import JobPosting, JobApplication, JobStatus
from config import Config

Base = declarative_base()

class JobApplicationRecord(Base):
    """SQLAlchemy model for job applications."""
    __tablename__ = "job_applications"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    job_title = Column(String, nullable=False)
    company_name = Column(String, nullable=False)
    job_description = Column(Text)
    job_requirements = Column(Text)
    posting_url = Column(String)
    location = Column(String)
    salary_range = Column(String)
    job_type = Column(String)
    remote_ok = Column(Boolean, default=False)
    source = Column(String)
    posted_date = Column(DateTime)
    scraped_date = Column(DateTime, default=datetime.utcnow)
    
    status = Column(String, default=JobStatus.FOUND.value)
    applied_date = Column(DateTime)
    resume_path = Column(String)
    cover_letter_path = Column(String)
    notes = Column(Text)
    follow_up_date = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class TrackerAgent(BaseAgent):
    """
    Agent responsible for tracking and managing job applications.
    Uses OpenAI to help with application insights and recommendations.
    """
    
    def __init__(self):
        system_prompt = """
        You are a job application tracking and analytics specialist. Your role is to:
        
        1. Track job application status and progress across multiple applications
        2. Analyze application patterns and success rates
        3. Provide insights on application strategy and timing
        4. Generate reports on job search progress and metrics
        5. Recommend follow-up actions and application optimizations
        
        When analyzing job applications:
        - Track key metrics like response rates, interview rates, and success patterns
        - Identify trends in successful applications (companies, roles, timing)
        - Suggest improvements to application strategy
        - Recommend optimal follow-up timing
        - Highlight gaps or opportunities in the job search
        
        Always provide actionable insights that help improve job search effectiveness.
        """
        super().__init__("Tracker", system_prompt)
        self.supported_functions = ["analyze_applications", "generate_insights", "recommend_actions"]
        
        # Initialize database
        self.engine = create_engine(Config.DATABASE_URL)
        Base.metadata.create_all(self.engine)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.db_session = SessionLocal()
    
    def execute_function(self, function_name: str, args: Dict[str, Any]) -> Any:
        """Execute specific tracking functions."""
        if function_name == "analyze_applications":
            return self._analyze_application_patterns(args.get("time_period", "all"))
        elif function_name == "generate_insights":
            return self._generate_job_search_insights()
        elif function_name == "recommend_actions":
            return self._recommend_follow_up_actions()
        else:
            raise ValueError(f"Unknown function: {function_name}")
    
    def process_request(self, request: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Process tracking requests."""
        try:
            request_lower = request.lower()
            
            if "track" in request_lower or "add" in request_lower:
                if context and "job_application" in context:
                    application = JobApplication(**context["job_application"])
                    tracked_app = self.track_application(application)
                    return AgentResponse(
                        success=True,
                        data={"application_id": tracked_app.id},
                        message="Successfully tracked job application"
                    )
            
            elif "update" in request_lower:
                if context and "application_id" in context:
                    app_id = context["application_id"]
                    updates = context.get("updates", {})
                    updated_app = self.update_application_status(app_id, updates)
                    return AgentResponse(
                        success=True,
                        data={"updated_application": self._application_to_dict(updated_app)},
                        message="Successfully updated application status"
                    )
            
            elif "analytics" in request_lower or "report" in request_lower:
                analytics = self.get_application_analytics()
                return AgentResponse(
                    success=True,
                    data={"analytics": analytics},
                    message="Successfully generated application analytics"
                )
            
            elif "insights" in request_lower:
                insights = self._generate_job_search_insights_with_ai()
                return AgentResponse(
                    success=True,
                    data={"insights": insights},
                    message="Successfully generated job search insights"
                )
            
            else:
                # Use OpenAI for general tracking questions
                messages = self._prepare_messages(request, context)
                response = self._make_openai_request(messages)
                return self._handle_response(response)
                
        except Exception as e:
            self.logger.error(f"Error processing tracking request: {str(e)}")
            return AgentResponse(
                success=False,
                message="Failed to process tracking request",
                errors=[str(e)]
            )
    
    def track_application(self, job_application: JobApplication) -> JobApplicationRecord:
        """
        Track a new job application in the database.
        
        Args:
            job_application: JobApplication object to track
            
        Returns:
            JobApplicationRecord that was created
        """
        try:
            # Create database record
            db_application = JobApplicationRecord(
                job_title=job_application.job_posting.title,
                company_name=job_application.job_posting.company,
                job_description=job_application.job_posting.description,
                job_requirements=job_application.job_posting.requirements,
                posting_url=str(job_application.job_posting.posting_url),
                location=job_application.job_posting.location,
                salary_range=job_application.job_posting.salary_range,
                job_type=job_application.job_posting.job_type,
                remote_ok=job_application.job_posting.remote_ok,
                source=job_application.job_posting.source,
                posted_date=job_application.job_posting.posted_date,
                scraped_date=job_application.job_posting.scraped_date,
                status=job_application.status.value,
                applied_date=job_application.applied_date,
                resume_path=job_application.resume_path,
                cover_letter_path=job_application.cover_letter_path,
                notes=job_application.notes,
                follow_up_date=job_application.follow_up_date
            )
            
            self.db_session.add(db_application)
            self.db_session.commit()
            
            self.logger.info(f"Tracked application: {db_application.company_name} - {db_application.job_title}")
            return db_application
            
        except Exception as e:
            self.db_session.rollback()
            self.logger.error(f"Error tracking application: {str(e)}")
            raise
    
    def update_application_status(self, application_id: str, updates: Dict[str, Any]) -> JobApplicationRecord:
        """
        Update the status of a tracked application.
        
        Args:
            application_id: ID of the application to update
            updates: Dictionary of fields to update
            
        Returns:
            Updated JobApplicationRecord
        """
        try:
            application = self.db_session.query(JobApplicationRecord).filter_by(id=application_id).first()
            
            if not application:
                raise ValueError(f"Application with ID {application_id} not found")
            
            # Update allowed fields
            allowed_fields = [
                'status', 'applied_date', 'resume_path', 'cover_letter_path', 
                'notes', 'follow_up_date'
            ]
            
            for field, value in updates.items():
                if field in allowed_fields:
                    setattr(application, field, value)
            
            application.updated_at = datetime.utcnow()
            self.db_session.commit()
            
            self.logger.info(f"Updated application {application_id}: {updates}")
            return application
            
        except Exception as e:
            self.db_session.rollback()
            self.logger.error(f"Error updating application: {str(e)}")
            raise
    
    def get_all_applications(self, status: Optional[JobStatus] = None) -> List[JobApplicationRecord]:
        """
        Get all tracked applications, optionally filtered by status.
        
        Args:
            status: Optional status filter
            
        Returns:
            List of JobApplicationRecord objects
        """
        try:
            query = self.db_session.query(JobApplicationRecord)
            
            if status:
                query = query.filter_by(status=status.value)
            
            applications = query.order_by(JobApplicationRecord.created_at.desc()).all()
            return applications
            
        except Exception as e:
            self.logger.error(f"Error getting applications: {str(e)}")
            return []
    
    def get_application_analytics(self) -> Dict[str, Any]:
        """
        Generate analytics on job applications.
        
        Returns:
            Dictionary containing various analytics metrics
        """
        try:
            all_apps = self.get_all_applications()
            
            if not all_apps:
                return {"message": "No applications tracked yet"}
            
            # Basic counts
            total_apps = len(all_apps)
            status_counts = {}
            
            for app in all_apps:
                status = app.status
                status_counts[status] = status_counts.get(status, 0) + 1
            
            # Response rates
            applied_count = status_counts.get(JobStatus.APPLIED.value, 0)
            interview_count = status_counts.get(JobStatus.INTERVIEW_SCHEDULED.value, 0) + \
                            status_counts.get(JobStatus.INTERVIEWED.value, 0)
            offer_count = status_counts.get(JobStatus.OFFERED.value, 0) + \
                         status_counts.get(JobStatus.ACCEPTED.value, 0)
            
            # Company and source analysis
            company_counts = {}
            source_counts = {}
            
            for app in all_apps:
                company_counts[app.company_name] = company_counts.get(app.company_name, 0) + 1
                source_counts[app.source] = source_counts.get(app.source, 0) + 1
            
            # Time analysis
            recent_apps = [app for app in all_apps if app.created_at >= datetime.utcnow() - timedelta(days=30)]
            
            analytics = {
                "total_applications": total_apps,
                "status_breakdown": status_counts,
                "metrics": {
                    "response_rate": (interview_count / applied_count * 100) if applied_count > 0 else 0,
                    "interview_rate": (interview_count / applied_count * 100) if applied_count > 0 else 0,
                    "offer_rate": (offer_count / applied_count * 100) if applied_count > 0 else 0
                },
                "top_companies": dict(sorted(company_counts.items(), key=lambda x: x[1], reverse=True)[:10]),
                "source_breakdown": source_counts,
                "recent_activity": {
                    "last_30_days": len(recent_apps),
                    "avg_per_week": len(recent_apps) / 4.3 if recent_apps else 0
                }
            }
            
            return analytics
            
        except Exception as e:
            self.logger.error(f"Error generating analytics: {str(e)}")
            return {"error": str(e)}
    
    def get_follow_up_recommendations(self) -> List[Dict[str, Any]]:
        """
        Get applications that need follow-up.
        
        Returns:
            List of applications requiring follow-up
        """
        try:
            today = datetime.utcnow().date()
            
            # Applications needing follow-up
            follow_up_apps = self.db_session.query(JobApplicationRecord).filter(
                JobApplicationRecord.follow_up_date <= today,
                JobApplicationRecord.status.in_([JobStatus.APPLIED.value, JobStatus.INTERVIEWED.value])
            ).all()
            
            # Applications applied > 1 week ago without response
            one_week_ago = datetime.utcnow() - timedelta(days=7)
            stale_apps = self.db_session.query(JobApplicationRecord).filter(
                JobApplicationRecord.applied_date <= one_week_ago,
                JobApplicationRecord.status == JobStatus.APPLIED.value
            ).all()
            
            recommendations = []
            
            for app in follow_up_apps:
                recommendations.append({
                    "application_id": app.id,
                    "company": app.company_name,
                    "position": app.job_title,
                    "reason": "Scheduled follow-up date reached",
                    "priority": "high",
                    "action": "Send follow-up email"
                })
            
            for app in stale_apps:
                if app not in follow_up_apps:
                    recommendations.append({
                        "application_id": app.id,
                        "company": app.company_name,
                        "position": app.job_title,
                        "reason": "No response for over a week",
                        "priority": "medium",
                        "action": "Consider following up"
                    })
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error getting follow-up recommendations: {str(e)}")
            return []
    
    def _generate_job_search_insights_with_ai(self) -> Dict[str, Any]:
        """
        Generate insights about job search progress using OpenAI.
        """
        try:
            analytics = self.get_application_analytics()
            follow_ups = self.get_follow_up_recommendations()
            
            prompt = f"""
            Analyze this job search data and provide insights and recommendations:
            
            Application Analytics:
            {json.dumps(analytics, indent=2, default=str)}
            
            Follow-up Recommendations:
            {json.dumps(follow_ups, indent=2)}
            
            Please provide:
            1. Key insights about the job search performance
            2. Strengths and areas for improvement
            3. Specific recommendations for better results
            4. Strategy adjustments based on the data
            5. Timeline and goal suggestions
            
            Format as a JSON object with sections: insights, strengths, improvements, recommendations, strategy.
            """
            
            messages = self._prepare_messages(prompt)
            response = self._make_openai_request(messages)
            
            if response["choices"][0]["message"]["content"]:
                content = response["choices"][0]["message"]["content"]
                
                try:
                    # Extract JSON from the response
                    start = content.find("{")
                    end = content.rfind("}") + 1
                    json_str = content[start:end]
                    insights = json.loads(json_str)
                    
                    return insights
                    
                except json.JSONDecodeError:
                    # Fallback to basic insights
                    return self._generate_basic_insights(analytics, follow_ups)
            
        except Exception as e:
            self.logger.error(f"Error generating AI insights: {str(e)}")
            return self._generate_basic_insights(analytics if 'analytics' in locals() else {}, 
                                               follow_ups if 'follow_ups' in locals() else [])
    
    def _generate_basic_insights(self, analytics: Dict[str, Any], follow_ups: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate basic insights as fallback.
        """
        total_apps = analytics.get("total_applications", 0)
        
        insights = {
            "insights": [
                f"You have tracked {total_apps} job applications so far",
                f"You have {len(follow_ups)} applications that may need follow-up",
            ],
            "strengths": ["Consistent application tracking"],
            "improvements": ["Consider following up on stale applications"],
            "recommendations": [
                "Set follow-up reminders for all applications",
                "Track response rates to optimize your approach"
            ],
            "strategy": "Continue applying consistently and maintain good tracking habits"
        }
        
        if total_apps > 10:
            response_rate = analytics.get("metrics", {}).get("response_rate", 0)
            if response_rate < 10:
                insights["improvements"].append("Low response rate - consider improving resume/cover letter")
            elif response_rate > 20:
                insights["strengths"].append("Good response rate - current approach is working")
        
        return insights
    
    def _analyze_application_patterns(self, time_period: str) -> Dict[str, Any]:
        """Analyze patterns in job applications."""
        return {"analysis": "Pattern analysis would go here"}
    
    def _generate_job_search_insights(self) -> Dict[str, Any]:
        """Generate job search insights."""
        return {"insights": "Job search insights would go here"}
    
    def _recommend_follow_up_actions(self) -> List[Dict[str, Any]]:
        """Recommend follow-up actions."""
        return self.get_follow_up_recommendations()
    
    def _application_to_dict(self, app: JobApplicationRecord) -> Dict[str, Any]:
        """Convert JobApplicationRecord to dictionary."""
        return {
            "id": app.id,
            "company": app.company_name,
            "title": app.job_title,
            "status": app.status,
            "applied_date": app.applied_date.isoformat() if app.applied_date else None,
            "created_at": app.created_at.isoformat(),
            "updated_at": app.updated_at.isoformat()
        }
    
    def __del__(self):
        """Clean up database session."""
        if hasattr(self, 'db_session'):
            self.db_session.close()