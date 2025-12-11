import sqlite3
import json
from src.profile_manager import load_profile
from src.resume_tailor import ResumeTailor # To reuse keyword extraction and scoring

DATABASE_NAME = 'jobs.db'

class JobDatabase:
    def __init__(self):
        self.conn = sqlite3.connect(DATABASE_NAME)
        self.cursor = self.conn.cursor()
        self._create_table()

    def _create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company TEXT NOT NULL,
                role TEXT NOT NULL,
                location TEXT,
                link TEXT,
                date_posted TEXT,
                original_category TEXT,
                fit_score REAL,
                fit_category TEXT,
                status TEXT DEFAULT 'new',
                raw_data TEXT
            )
        ''')
        self.conn.commit()

    def insert_job(self, job_data):
        """Inserts a single job into the database."""
        # Ensure job_data has all expected keys, provide defaults if missing
        job_data.setdefault('company', 'N/A')
        job_data.setdefault('role', 'N/A')
        job_data.setdefault('location', 'N/A')
        job_data.setdefault('link', 'N/A')
        job_data.setdefault('date_posted', 'N/A')
        job_data.setdefault('original_category', 'N/A')
        job_data.setdefault('fit_score', -1.0)
        job_data.setdefault('fit_category', 'unclassified')
        job_data.setdefault('status', 'new')
        job_data.setdefault('raw_data', json.dumps(job_data)) # Store original data for debugging

        self.cursor.execute('''
            INSERT INTO jobs (company, role, location, link, date_posted, original_category, fit_score, fit_category, status, raw_data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            job_data['company'],
            job_data['role'],
            job_data['location'],
            job_data['link'],
            job_data['date_posted'],
            job_data['original_category'],
            job_data['fit_score'],
            job_data['fit_category'],
            job_data['status'],
            job_data['raw_data']
        ))
        self.conn.commit()
        return self.cursor.lastrowid

    def insert_jobs(self, jobs_list):
        """Inserts a list of jobs into the database, avoiding duplicates based on link and role."""
        inserted_count = 0
        for job_data in jobs_list:
            # Check for existing job with same link and role
            self.cursor.execute('SELECT id FROM jobs WHERE link = ? AND role = ?', (job_data.get('link'), job_data.get('role')))
            existing_job = self.cursor.fetchone()
            if existing_job:
                # print(f"Job '{job_data.get('role')}' at {job_data.get('company')}' already exists, skipping.")
                continue
            self.insert_job(job_data)
            inserted_count += 1
        return inserted_count


    def get_jobs(self, status=None, fit_category=None):
        """Retrieves jobs based on status and/or fit_category."""
        query = 'SELECT id, company, role, location, link, fit_category, status FROM jobs WHERE 1=1'
        params = []
        if status:
            query += ' AND status = ?'
            params.append(status)
        if fit_category:
            query += ' AND fit_category = ?'
            params.append(fit_category)
        
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def get_job_by_id(self, job_id):
        """Retrieves a single job by its ID."""
        self.cursor.execute('SELECT * FROM jobs WHERE id = ?', (job_id,))
        # Fetch column names to return dictionary-like results
        columns = [description[0] for description in self.cursor.description]
        row = self.cursor.fetchone()
        if row:
            return dict(zip(columns, row))
        return None

    def update_job_status(self, job_id, new_status):
        """Updates the status of a specific job."""
        self.cursor.execute('UPDATE jobs SET status = ? WHERE id = ?', (new_status, job_id))
        self.conn.commit()

    def update_job_fit_score_and_category(self, job_id, fit_score, fit_category):
        """Updates the fit score and category of a specific job."""
        self.cursor.execute('UPDATE jobs SET fit_score = ?, fit_category = ? WHERE id = ?', (fit_score, fit_category, job_id))
        self.conn.commit()

    def close(self):
        """Closes the database connection."""
        self.conn.close()


def categorize_jobs(jobs_list, profile_name, high_threshold=5, medium_threshold=2):
    """
    Categorizes a list of jobs based on fit with the user's profile.
    
    Args:
        jobs_list (list): List of job dictionaries.
        profile_name (str): Name of the user's profile to load.
        high_threshold (int): Minimum score for 'High Fit'.
        medium_threshold (int): Minimum score for 'Medium Fit'.
        
    Returns:
        list: Jobs with added 'fit_score' and 'fit_category'.
    """
    try:
        tailor = ResumeTailor(profile_name)
    except ValueError as e:
        print(f"Error loading profile for categorization: {e}")
        return []

    categorized_jobs = []
    for job in jobs_list:
        job_description_parts = []
        # Combine relevant fields for keyword extraction
        if job.get('role'): job_description_parts.append(job['role'])
        if job.get('company'): job_description_parts.append(job['company'])
        # if job.get('Description'): job_description_parts.append(job['Description']) # if available from scraper
        
        # Use the _extract_keywords_from_job_description from ResumeTailor
        job_keywords = tailor._extract_keywords_from_job_description(" ".join(job_description_parts))
        
        # Calculate score from profile_data's skills, work_experience, projects
        score = 0
        
        # Score from skills
        for category, skills_list in tailor.profile_data["skills"].items():
            score += tailor._calculate_keyword_score(skills_list, job_keywords)
        
        # Score from work experience descriptions and technologies
        for exp in tailor.profile_data["work_experience"]:
            exp_text = exp.get("description", []) + exp.get("technologies", [])
            score += tailor._calculate_keyword_score(exp_text, job_keywords)

        # Score from projects descriptions and technologies
        for proj in tailor.profile_data["projects"]:
            proj_text = proj.get("description", []) + proj.get("technologies", [])
            score += tailor._calculate_keyword_score(proj_text, job_keywords)
            
        job['fit_score'] = score
        
        if score >= high_threshold:
            job['fit_category'] = 'High Fit'
        elif score >= medium_threshold:
            job['fit_category'] = 'Medium Fit'
        else:
            job['fit_category'] = 'Low Fit'
        
        categorized_jobs.append(job)
        
    return categorized_jobs

# Example usage (for testing purposes)
if __name__ == '__main__':
    # Initialize DB
    db = JobDatabase()

    # Create a dummy profile for testing categorization
    # For a real test, you'd create this via profile_manager.py
    # or have a dummy_profile.json
    dummy_profile_data = {
        "personal_info": {
            "name": "Test User",
            "email": "test@example.com",
            "phone": "123-456-7890",
            "linkedin": "http://linkedin.com/in/test",
            "github": "http://github.com/test"
        },
        "education": [],
        "work_experience": [
            {"title": "Software Engineer", "company": "Tech Corp", "start_date": "2020-01-01", "description": ["Developed Python applications.", "Used SQL databases."], "technologies": ["Python", "SQL"]},
            {"title": "Intern", "company": "Data Inc.", "start_date": "2019-06-01", "description": ["Analyzed data.", "Built dashboards with Tableau."], "technologies": ["Python", "Tableau"]}
        ],
        "projects": [
            {"name": "ML Project", "start_date": "2021-01-01", "description": ["Implemented machine learning models."], "technologies": ["Python", "Scikit-learn"]},
            {"name": "Web Scraper", "start_date": "2020-05-01", "description": ["Scraped data from websites."], "technologies": ["Python", "BeautifulSoup"]}
        ],
        "skills": {
            "Programming Languages": ["Python", "Java", "JavaScript"],
            "Databases": ["SQL", "PostgreSQL"],
            "Tools": ["Docker", "Git"]
        }
    }
    
    # Ensure a dummy profile exists for testing
    dummy_profile_name = "test_profile_for_jobs"
    try:
        from src.profile_manager import save_profile
        success, msg = save_profile(dummy_profile_name, dummy_profile_data)
        if not success:
            print(f"Could not save dummy profile: {msg}")
            # If profile exists and is valid, load_profile will return it.
    except Exception as e:
        print(f"Error setting up dummy profile: {e}")


    # Dummy job data from scraper
    dummy_jobs = [
        {'Company': 'Google', 'Role': 'Software Engineer', 'Location': 'Mountain View, CA', 'Link': 'http://google.com/job1', 'Date Posted': '2023-10-26', 'category': 'Software Engineer New Grad'},
        {'Company': 'Microsoft', 'Role': 'Data Scientist', 'Location': 'Redmond, WA', 'Link': 'http://microsoft.com/job2', 'Date Posted': '2023-10-25', 'category': 'Data Science New Grad'},
        {'Company': 'Amazon', 'Role': 'Web Developer', 'Location': 'Seattle, WA', 'Link': 'http://amazon.com/job3', 'Date Posted': '2023-10-24', 'category': 'Software Engineer New Grad'},
        {'Company': 'Meta', 'Role': 'ML Engineer', 'Location': 'Menlo Park, CA', 'Link': 'http://meta.com/job4', 'Date Posted': '2023-10-23', 'category': 'AI & Machine Learning New Grad', 'Description': 'Experience with Python and ML models required.'}
    ]

    print("\n--- Categorizing Jobs ---")
    categorized_dummy_jobs = categorize_jobs(dummy_jobs, dummy_profile_name)
    for job in categorized_dummy_jobs:
        print(f"Company: {job.get('Company')}, Role: {job.get('Role')}, Fit: {job.get('fit_category')} (Score: {job.get('fit_score')})")

    print("\n--- Inserting Categorized Jobs ---")
    db.insert_jobs(categorized_dummy_jobs)
    print(f"Inserted {len(categorized_dummy_jobs)} jobs.")

    print("\n--- Retrieving Jobs ---")
    all_jobs = db.get_jobs()
    print(f"Total jobs in DB: {len(all_jobs)}")
    for job in all_jobs:
        print(f"ID: {job[0]}, Company: {job[1]}, Role: {job[2]}, Fit: {job[5]}, Status: {job[6]}")

    print("\n--- Retrieving High Fit Jobs ---")
    high_fit_jobs = db.get_jobs(fit_category='High Fit')
    for job in high_fit_jobs:
        print(f"ID: {job[0]}, Company: {job[1]}, Role: {job[2]}")

    print("\n--- Updating Job Status ---")
    if all_jobs:
        first_job_id = all_jobs[0][0]
        db.update_job_status(first_job_id, 'applied')
        updated_job = db.get_job_by_id(first_job_id)
        print(f"Updated job ID {first_job_id} status to: {updated_job['status']}")

    db.close()
    print("\nDatabase connection closed.")
