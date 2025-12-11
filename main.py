import os
import sys
import json

# Add src directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from src.profile_manager import main as profile_manager_main, list_profiles, create_new_profile, load_profile
from src.github_job_scraper import GitHubJobScraper
from src.job_database import JobDatabase, categorize_jobs
from src.job_selector import JobSelector
from src.application_workflow import ApplicationWorkflow

def clear_screen():
    """Clears the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def select_or_create_profile():
    """Guides the user to select an existing profile or create a new one."""
    while True:
        profiles = list_profiles()
        if not profiles:
            print("\nNo profiles found. Let's create one.")
            profile_name = input("Enter a name for your new profile: ")
            success, message = create_new_profile(profile_name)
            print(message)
            if success:
                return profile_name
        else:
            print("\nPlease select a profile or create a new one:")
            for i, p in enumerate(profiles):
                print(f"{i+1}. {p}")
            print(f"{len(profiles)+1}. Create New Profile")
            print("Enter 'm' to manage profiles (full manager menu).")
            
            choice = input("Enter your choice: ").strip()

            if choice.lower() == 'm':
                profile_manager_main() # Call the full profile manager CLI
                continue # Redisplay profile selection after managing
            
            try:
                choice_idx = int(choice)
                if 1 <= choice_idx <= len(profiles):
                    return profiles[choice_idx - 1]
                elif choice_idx == len(profiles) + 1:
                    profile_name = input("Enter a name for your new profile: ")
                    success, message = create_new_profile(profile_name)
                    print(message)
                    if success:
                        return profile_name
                else:
                    print("Invalid choice. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a number or 'm'.")

def main():
    clear_screen()
    print("--- Gemini AI Automated Job Application CLI ---")

    # 1. Select or Create Profile
    selected_profile_name = select_or_create_profile()
    if not selected_profile_name:
        print("No profile selected. Exiting.")
        return
    
    profile_data, error = load_profile(selected_profile_name)
    if error:
        print(f"Error loading selected profile '{selected_profile_name}': {error}. Exiting.")
        return

    print(f"\nUsing profile: {selected_profile_name}")

    db = JobDatabase()
    scraper = GitHubJobScraper()
    selector = JobSelector()

    try:
        while True:
            print("\n--- Main Menu ---")
            print("1. Scrape New Jobs")
            print("2. View and Select Job for Application")
            print("3. Manage Profiles")
            print("4. Exit")

            choice = input("Enter your choice: ").strip()

            if choice == '1':
                print("\nScraping jobs from GitHub repository...")
                scraped_jobs = scraper.get_jobs()
                if scraped_jobs:
                    print(f"Found {len(scraped_jobs)} raw jobs.")
                    # Categorize and insert only if job database is empty or if we want to update
                    # For now, let's categorize and insert
                    categorized_jobs = categorize_jobs(scraped_jobs, selected_profile_name)
                    inserted_count = db.insert_jobs(categorized_jobs)
                    print(f"Inserted {inserted_count} new unique jobs into the database.")
                else:
                    print("No jobs scraped or an error occurred.")

            elif choice == '2':
                selected_job = selector.display_and_select_job()
                if selected_job:
                    workflow = ApplicationWorkflow(selected_profile_name)
                    workflow.execute_application_flow(selected_job)
                    workflow.close() # Close workflow's DB connection
                    print("\nReturning to main menu.")
                else:
                    print("\nNo job selected. Returning to main menu.")

            elif choice == '3':
                profile_manager_main() # Allow managing profiles without exiting main loop
            
            elif choice == '4':
                print("Exiting application. Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")

    finally:
        db.close()
        selector.close() # Close selector's DB connection (it uses a separate instance)


if __name__ == '__main__':
    main()
