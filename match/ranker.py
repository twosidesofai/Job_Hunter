import json
from typing import List, Dict

def rank_jobs(jobs: List[Dict], profile: Dict) -> List[Dict]:
    # Weight features: title match, skill overlap, seniority, location/remote, compensation fit
    ranked = []
    for job in jobs:
        score = 0
        rationale = []
        # Title match
        if job.get('title', '').lower() in [t.lower() for t in profile.get('job_prefs', {}).get('titles', [])]:
            score += 3
            rationale.append('Title match')
        # Skill overlap
        skills = set([s.lower() for s in profile.get('skills', [])])
        job_skills = set([s.lower() for s in job.get('skills', [])])
        overlap = len(skills & job_skills)
        score += overlap
        if overlap:
            rationale.append(f"{overlap} skill(s) matched")
        # Seniority
        if 'senior' in job.get('title', '').lower():
            score += 2
            rationale.append('Seniority match')
        # Location/remote
        if job.get('location', '').lower() in [l.lower() for l in profile.get('job_prefs', {}).get('locations', [])]:
            score += 2
            rationale.append('Location match')
        if job.get('remote', False) and profile.get('job_prefs', {}).get('remote_ok', False):
            score += 2
            rationale.append('Remote OK')
        # Compensation fit
        if job.get('salary_min', 0) >= profile.get('job_prefs', {}).get('salary_min', 0):
            score += 1
            rationale.append('Salary fit')
        job['score'] = score
        job['rationale'] = rationale
        ranked.append(job)
    # Sort by score descending
    return sorted(ranked, key=lambda x: x['score'], reverse=True)

# Unit test
if __name__ == "__main__":
    profile = {
        "skills": ["Python", "ML", "APIs"],
        "job_prefs": {"titles": ["Engineer"], "locations": ["Remote"], "remote_ok": True, "salary_min": 100000}
    }
    jobs = [
        {"title": "Engineer", "skills": ["Python", "APIs"], "location": "Remote", "remote": True, "salary_min": 120000},
        {"title": "Manager", "skills": ["Excel"], "location": "NYC", "remote": False, "salary_min": 90000}
    ]
    ranked = rank_jobs(jobs, profile)
    for job in ranked:
        print(job)
