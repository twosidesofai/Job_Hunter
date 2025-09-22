# tracker.py
"""
Logs and tracks job applications in a local database.
"""


import sqlite3
from datetime import datetime
from typing import Optional, List, Dict

# Tracker agent for SQLite
class TrackerAgent:
	def __init__(self, db_path: str = "applications.db"):
		self.db_path = db_path
		self._init_db()

	def _init_db(self):
		with sqlite3.connect(self.db_path) as conn:
			c = conn.cursor()
			c.execute('''
				CREATE TABLE IF NOT EXISTS applications (
					id INTEGER PRIMARY KEY AUTOINCREMENT,
					company TEXT,
					job_title TEXT,
					url TEXT,
					applied_at TEXT,
					status TEXT
				)
			''')
			conn.commit()

	def log_application(self, company: str, job_title: str, url: str, status: str = "applied"):
		applied_at = datetime.utcnow().isoformat()
		with sqlite3.connect(self.db_path) as conn:
			c = conn.cursor()
			c.execute('''
				INSERT INTO applications (company, job_title, url, applied_at, status)
				VALUES (?, ?, ?, ?, ?)
			''', (company, job_title, url, applied_at, status))
			conn.commit()

	def update_status(self, app_id: int, status: str):
		with sqlite3.connect(self.db_path) as conn:
			c = conn.cursor()
			c.execute('''
				UPDATE applications SET status = ? WHERE id = ?
			''', (status, app_id))
			conn.commit()

	def get_applications(self, status: Optional[str] = None) -> List[Dict]:
		with sqlite3.connect(self.db_path) as conn:
			c = conn.cursor()
			if status:
				c.execute('SELECT * FROM applications WHERE status = ?', (status,))
			else:
				c.execute('SELECT * FROM applications')
			rows = c.fetchall()
			columns = [desc[0] for desc in c.description]
			return [dict(zip(columns, row)) for row in rows]

# Example usage (for testing)
if __name__ == "__main__":
	tracker = TrackerAgent()
	tracker.log_application("TechCorp", "Software Engineer", "https://linkedin.com/jobs/123")
	tracker.log_application("Indeed", "Backend Developer", "https://indeed.com/jobs/456", status="interview")
	tracker.update_status(1, "offer")
	apps = tracker.get_applications()
	for app in apps:
		print(app)
