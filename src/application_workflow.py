import json
import os
from src.profile_manager import load_profile
from src.resume_tailor import ResumeTailor
from src.pdf_renderer import PDFRenderer
from src.job_database import JobDatabase

class ApplicationWorkflow:
    def __init__(self, profile_name):
        self.profile_name = profile_name
        self.db = JobDatabase()
        self.pdf_renderer = PDFRenderer()
        try:
            self.resume_tailor = ResumeTailor(profile_name)
        except ValueError as e:
            print(f"Error initializing ResumeTailor: {e}")
            self.resume_tailor = None

    def execute_application_flow(self, selected_job):
        """
        Executes the job application flow for a selected job, including tailoring, approval, and (eventually) submission.
        """
        if not self.resume_tailor:
            print("Cannot proceed: ResumeTailor not initialized due to profile error.")
            return False

        print(f"\n--- Initiating application for: {selected_job['role']} at {selected_job['company']} ---")
        print(f"Job Link: {selected_job['link']}")

        # Step 1: Tailor Resume
        print("\n--- Tailoring Resume ---")
        job_description = f"{selected_job['role']} {selected_job['company']} {selected_job.get('location', '')}"
        # For a more robust tailoring, we would ideally fetch the full job description from the link
        # For now, we'll use the available job data for keyword extraction.
        
        # This will be enhanced later to fetch the full job description from the 'link'
        # For now, let's use a combination of role, company and available raw_data
        full_job_description_text = f"{selected_job['role']} {selected_job['company']}"
        if selected_job.get('raw_data'):
            raw_data = json.loads(selected_job['raw_data'])
            # Assuming 'Description' or similar field might be present in raw_data from scraper
            if raw_data.get('Description'):
                full_job_description_text += f" {raw_data['Description']}"
            elif raw_data.get('description'):
                 full_job_description_text += f" {raw_data['description']}"
            # Add other relevant fields for better tailoring
            for key in ['location', 'requirements', 'qualifications', 'responsibilities']:
                if raw_data.get(key):
                    full_job_description_text += f" {raw_data[key]}"


        tailored_resume_data = self.resume_tailor.tailor_resume(full_job_description_text)
        tailored_resume_markdown = self.resume_tailor.format_to_markdown(tailored_resume_data)

        print("\n--- Tailored Resume Preview (Markdown) ---")
        print(tailored_resume_markdown)
        print("------------------------------------------")

        # Step 2: User Approval
        approval = input("Do you approve this tailored resume and wish to proceed with the application? (yes/no): ").lower().strip()
        if approval != 'yes':
            print("Application cancelled by user.")
            self.db.update_job_status(selected_job['id'], 'tailoring_rejected')
            return False

        # Step 3: Render to PDF
        output_dir = os.path.join(os.path.dirname(__file__), '..', 'output_resumes')
        os.makedirs(output_dir, exist_ok=True)
        
        # Sanitize filename for output
        safe_company_name = "".join(c for c in selected_job['company'] if c.isalnum() or c in (' ', '_')).rstrip()
        safe_role_name = "".join(c for c in selected_job['role'] if c.isalnum() or c in (' ', '_')).rstrip()
        
        pdf_filename = f"{self.profile_name}_{safe_company_name}_{safe_role_name}.pdf"
        output_filepath = os.path.join(output_dir, pdf_filename)

        print(f"\n--- Rendering PDF to {output_filepath} ---")
        success, message = self.pdf_renderer.render_markdown_to_pdf(tailored_resume_markdown, output_filepath)
        if success:
            print(message)
            self.db.update_job_status(selected_job['id'], 'resume_tailored')
            # At this point, the tailored resume PDF is ready.
            # Next would be browser automation for application submission (Phase 3.2, 3.3)
            return True
        else:
            print(f"Failed to render PDF: {message}")
            self.db.update_job_status(selected_job['id'], 'pdf_render_failed')
            return False

    def close(self):
        self.db.close()

# Example usage (for testing purposes)
if __name__ == '__main__':
    # This example assumes you have a profile named 'my_profile' and some jobs in jobs.db
    # To run this, you'd typically:
    # 1. Run profile_manager.py to create a profile (e.g., 'my_profile').
    # 2. Run github_job_scraper.py to get jobs.
    # 3. Run job_database.py (main section) to categorize and insert jobs.
    # 4. Run job_selector.py to select a job.
    # Then pass the selected job to this script.
    
    # For a quick test, let's try to get a dummy job from the DB
    test_db = JobDatabase()
    all_jobs_in_db = test_db.get_jobs()
    test_db.close()

    if all_jobs_in_db:
        # Just pick the first one for testing purposes
        # In a real scenario, this would come from JobSelector
        selected_job_for_test = test_db.get_job_by_id(all_jobs_in_db[0][0]) 
        
        if selected_job_for_test:
            workflow = ApplicationWorkflow(profile_name="test_profile_for_jobs") # Use the dummy profile created by job_database.py example
            workflow.execute_application_flow(selected_job_for_test)
            workflow.close()
        else:
            print("Could not retrieve selected job for test.")
    else:
        print("No jobs in database. Please run scraper and database population first.")
