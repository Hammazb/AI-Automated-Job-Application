# AI-Automated Job Application CLI

## Description

This project is a command-line interface (CLI) agent that automates the process of finding and applying for jobs. It scrapes job listings from a specified GitHub repository, categorizes them based on your professional profile, helps you select a job, tailors your resume for that specific job, and prepares it as a PDF.

## Features

*   **Automated Job Scraping:** Scrapes job listings from the [SimplifyJobs/New-Grad-Positions](https://github.com/SimplifyJobs/New-Grad-Positions) GitHub repository.
*   **Profile Management:** Manages a user's professional profile (resume data) in a structured JSON format.
*   **Job Categorization:** Automatically categorizes scraped jobs into "High Fit," "Medium Fit," and "Low Fit" based on your profile.
*   **Resume Tailoring:** Dynamically tailors your master resume for each specific job application by selecting and reordering relevant experiences and skills.
*   **PDF Generation:** Renders the tailored resume into a professional-looking PDF file.
*   **Interactive CLI:** Provides a user-friendly command-line interface to manage the entire workflow.

## Workflow

1.  **Scrape Jobs:** The agent fetches the latest job postings from the specified GitHub repository.
2.  **Categorize Jobs:** It then analyzes these jobs and categorizes them based on how well they match your stored professional profile.
3.  **Select a Job:** You are presented with a categorized list of jobs and can select one to apply for.
4.  **Tailor Resume:** The agent generates a custom resume tailored to the keywords and requirements of the selected job.
5.  **Approve and Render:** You review the tailored resume. Upon approval, the agent renders it as a PDF file, ready for submission.

## Installation

### Prerequisites

*   Python 3.x
*   `pip` (Python package installer)
*   `wkhtmltopdf`: This is a command-line tool required for PDF generation.

### Steps

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/bhargav-modupalli/AI-Automated-Job-Application.git
    cd AI-Automated-Job-Application
    ```

2.  **Install `wkhtmltopdf`:**
    *   Download the installer for your operating system from the official website: [https://wkhtmltopdf.org/downloads.html](https://wkhtmltopdf.org/downloads.html)
    *   Run the installer. On Windows, it's recommended to install it to the default location (`C:\Program Files\wkhtmltopdf`). The script will automatically try to find it there. For other operating systems, ensure the `wkhtmltopdf` executable is in your system's `PATH`.

3.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  **Run the application:**
    ```bash
    python main.py
    ```

2.  **Profile Setup:**
    *   If you're running the application for the first time, it will prompt you to create a new profile.
    *   Follow the on-screen instructions to enter your personal information, education, work experience, projects, and skills.
    *   Your profile will be saved as a JSON file in the `profiles/` directory.

3.  **Main Menu:**
    *   **Scrape New Jobs:** Fetches the latest job listings and adds them to the local database.
    *   **View and Select Job for Application:** Displays the scraped jobs, categorized by how well they fit your profile. You can then select a job to start the tailoring and application process.
    *   **Manage Profiles:** Allows you to create new profiles or edit existing ones.
    *   **Exit:** Exits the application.

## Dependencies

### Python Libraries

The following Python libraries are required and will be installed via `pip install -r requirements.txt`:

*   `jsonschema`: For validating the profile data structure.
*   `markdown`: For converting Markdown to HTML.
*   `pdfkit`: A wrapper for `wkhtmltopdf` to generate PDFs from HTML.
*   `requests`: For fetching data from the web (e.g., the job listings).
*   `python-dotenv`: For managing environment variables (if any).
*   `beautifulsoup4`: For parsing HTML content.
*   `lxml`: An efficient XML/HTML parser used by BeautifulSoup.

### External Tools

*   `wkhtmltopdf`: The command-line tool that `pdfkit` uses to generate PDFs.

## Project Structure

```
AI-Automated-Job-Application/
├── src/
│   ├── __init__.py
│   ├── application_workflow.py   # Orchestrates the application process
│   ├── github_job_scraper.py     # Scrapes jobs from GitHub
│   ├── job_database.py           # Manages the SQLite job database
│   ├── job_selector.py           # Handles the job selection UI
│   ├── pdf_renderer.py           # Renders Markdown/HTML to PDF
│   └── profile_manager.py        # Manages user profiles
├── schemas/
│   └── profile_schema.json       # JSON schema for user profiles
├── main.py                       # Main entry point for the CLI application
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

---
*This project is a demonstration and may require further development for production use, especially regarding browser automation for form submission.*
