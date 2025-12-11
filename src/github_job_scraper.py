import requests
from bs4 import BeautifulSoup
import json
import os
import re

class GitHubJobScraper:
    def __init__(self, repo_owner="SimplifyJobs", repo_name="New-Grad-Positions", branch="dev"):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.branch = branch
        self.readme_url = f"https://raw.githubusercontent.com/{self.repo_owner}/{self.repo_name}/{self.branch}/README.md"
        # The actual content served from raw.githubusercontent.com for this repo is often rendered HTML from the markdown.

    def fetch_content(self):
        """Fetches the content (assumed to be HTML) of the README.md file."""
        try:
            response = requests.get(self.readme_url)
            response.raise_for_status()  # Raise an exception for HTTP errors
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error fetching README content from {self.readme_url}: {e}")
            return None

    def parse_jobs_from_html(self, html_content):
        """
        Parses job listings from the HTML content, assuming they are within tables.
        """
        jobs = []
        soup = BeautifulSoup(html_content, 'lxml')

        # Find all tables in the HTML
        tables = soup.find_all('table')

        for table in tables:
            # Try to infer category from preceding h3 tag
            current_category_tag = table.find_previous_sibling('h3')
            current_category = current_category_tag.get_text(strip=True) if current_category_tag else "Uncategorized"

            headers = [th.get_text(strip=True) for th in table.find('thead').find_all('th')]
            
            # Map headers to more friendly keys, handling potential inconsistencies
            header_map = {
                'Company': 'company',
                'Role': 'role',
                'Location': 'location',
                'Application': 'link', # This will need special handling to extract actual link
                'Age': 'date_posted',
                # Add other potential headers and their mappings
            }
            
            mapped_headers = [header_map.get(h, h.lower().replace(' ', '_')) for h in headers]

            for row in table.find('tbody').find_all('tr'):
                cells = row.find_all('td')
                if len(cells) == len(mapped_headers):
                    job_data = {}
                    for i, header in enumerate(mapped_headers):
                        cell_content = cells[i]
                        if header == 'link': # Special handling for the application link
                            link_tag = cell_content.find('a')
                            job_data[header] = link_tag['href'] if link_tag and 'href' in link_tag.attrs else cell_content.get_text(strip=True)
                        elif header == 'company': # Extract company name, remove any '🔥' or other emojis
                            company_text = cell_content.get_text(strip=True)
                            job_data[header] = re.sub(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002702-\U000027B0]', '', company_text).strip()
                        elif header == 'location': # Handle multiple locations from <details> tag if present
                            details_tag = cell_content.find('details')
                            if details_tag:
                                summary = details_tag.find('summary')
                                if summary and summary.strong:
                                    num_locations = int(summary.strong.get_text(strip=True).split(' ')[0])
                                    location_text = str(details_tag).split('</summary>')[-1].replace('<br/>', '\n').strip()
                                    job_data[header] = location_text
                                else:
                                    job_data[header] = cell_content.get_text(separator='\n', strip=True)
                            else:
                                job_data[header] = cell_content.get_text(separator='\n', strip=True) # Use \n for <br>
                        else:
                            job_data[header] = cell_content.get_text(strip=True)
                    
                    job_data['original_category'] = current_category # Add the inferred category
                    jobs.append(job_data)
        return jobs

    def get_jobs(self):
        """Fetches and parses job listings."""
        content = self.fetch_content()
        if content:
            return self.parse_jobs_from_html(content)
        return []

# Example usage (for testing purposes)
if __name__ == '__main__':
    scraper = GitHubJobScraper()
    job_listings = scraper.get_jobs()
    if job_listings:
        print(f"Found {len(job_listings)} job listings.")
        # Print a few jobs to verify parsing
        for i, job in enumerate(job_listings[:5]):
            print(f"\n--- Job {i+1} ---")
            print(json.dumps(job, indent=2))
    else:
        print("No job listings found or error occurred.")