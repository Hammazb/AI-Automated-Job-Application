import json
from src.job_database import JobDatabase

class JobSelector:
    def __init__(self):
        self.db = JobDatabase()

    def display_and_select_job(self):
        """
        Displays categorized jobs and allows the user to select one.
        Returns the selected job's data as a dictionary, or None if no job is selected.
        """
        jobs_by_category = {
            'High Fit': [],
            'Medium Fit': [],
            'Low Fit': [],
            'unclassified': []
        }

        # Retrieve all jobs, ordered by fit_score (descending) and then ID
        raw_jobs = self.db.cursor.execute('SELECT id, company, role, location, link, fit_category, fit_score FROM jobs ORDER BY fit_score DESC, id ASC').fetchall()
        
        # Convert to list of dicts for easier access and group by category
        columns = ['id', 'company', 'role', 'location', 'link', 'fit_category', 'fit_score']
        for job_tuple in raw_jobs:
            job = dict(zip(columns, job_tuple))
            jobs_by_category[job.get('fit_category', 'unclassified')].append(job)

        print("\n--- Available Job Listings ---")
        job_count = 0
        for category in ['High Fit', 'Medium Fit', 'Low Fit', 'unclassified']:
            if jobs_by_category[category]:
                print(f"\n### {category} Jobs ###")
                for job in jobs_by_category[category]:
                    job_count += 1
                    print(f"  [{job['id']}] {job['role']} at {job['company']} ({job['location']}) - Fit Score: {job['fit_score']:.2f}")
            
        if job_count == 0:
            print("No jobs found in the database. Please scrape jobs first.")
            return None

        while True:
            try:
                selected_id = input("\nEnter the ID of the job you want to select (or 'q' to quit): ").strip()
                if selected_id.lower() == 'q':
                    print("Job selection cancelled.")
                    return None
                
                selected_id = int(selected_id)
                selected_job = self.db.get_job_by_id(selected_id)

                if selected_job:
                    print(f"\nYou selected: {selected_job['role']} at {selected_job['company']}")
                    return selected_job
                else:
                    print("Invalid Job ID. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a number or 'q'.")

    def close(self):
        """Closes the database connection."""
        self.db.close()

# Example usage (for testing purposes)
if __name__ == '__main__':
    selector = JobSelector()
    selected_job_data = selector.display_and_select_job()
    if selected_job_data:
        print("\nSelected Job Details:")
        print(json.dumps(selected_job_data, indent=2))
    selector.close()
