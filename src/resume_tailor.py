import json
import os
from collections import defaultdict
from src.profile_manager import load_profile

class ResumeTailor:
    def __init__(self, profile_name):
        self.profile_data, error = load_profile(profile_name)
        if error:
            raise ValueError(f"Could not load profile '{profile_name}': {error}")
        if not self.profile_data:
            raise ValueError(f"Profile '{profile_name}' is empty or invalid.")

    def _calculate_keyword_score(self, text_list, keywords):
        """Calculates a score based on keyword matches in a list of strings."""
        score = 0
        text_content = " ".join(text_list).lower()
        for keyword in keywords:
            if keyword.lower() in text_content:
                score += 1
        return score

    def _extract_keywords_from_job_description(self, job_description):
        """
        Extracts keywords from a job description.
        Initially, this will be a simple tokenization.
        Later, this can be enhanced with NLP techniques.
        """
        # Simple tokenization for now
        return [word.lower() for word in job_description.split() if len(word) > 2]

    def tailor_resume(self, job_description):
        """
        Tailors the resume based on the job description.
        Returns a structured dictionary representing the tailored resume.
        """
        job_keywords = self._extract_keywords_from_job_description(job_description)
        tailored_resume = {
            "personal_info": self.profile_data["personal_info"],
            "education": self.profile_data["education"], # Education typically doesn't need tailoring
            "work_experience": [],
            "projects": [],
            "skills": defaultdict(list)
        }

        # Tailor Work Experience
        scored_experiences = []
        for exp in self.profile_data["work_experience"]:
            exp_text = [exp["title"], exp["company"]] + exp.get("description", []) + exp.get("technologies", [])
            score = self._calculate_keyword_score(exp_text, job_keywords)
            scored_experiences.append((score, exp))
        
        # Sort experiences by score (highest first)
        scored_experiences.sort(key=lambda x: x[0], reverse=True)
        tailored_resume["work_experience"] = [exp for score, exp in scored_experiences if score > 0 or len(scored_experiences) <= 3]
        # Include at least top 3 or all with score > 0

        # Tailor Projects
        scored_projects = []
        for proj in self.profile_data["projects"]:
            proj_text = [proj["name"]] + proj.get("description", []) + proj.get("technologies", [])
            score = self._calculate_keyword_score(proj_text, job_keywords)
            scored_projects.append((score, proj))

        # Sort projects by score
        scored_projects.sort(key=lambda x: x[0], reverse=True)
        tailored_resume["projects"] = [proj for score, proj in scored_projects if score > 0 or len(scored_projects) <= 2]
        # Include at least top 2 or all with score > 0

        # Tailor Skills (prioritize skills matching job keywords)
        for category, skills_list in self.profile_data["skills"].items():
            for skill in skills_list:
                if any(keyword.lower() in skill.lower() for keyword in job_keywords):
                    tailored_resume["skills"].insert(0, skill) # Add to front if it's a keyword match
                else:
                    tailored_resume["skills"].append(skill)
        
        return tailored_resume

    def format_to_markdown(self, tailored_resume_data):
        """
        Formats the tailored resume data into a Markdown string.
        This is a basic implementation and can be greatly enhanced.
        """
        md = f"# {tailored_resume_data['personal_info']['name']}\n\n"
        md += f"**Email:** {tailored_resume_data['personal_info']['email']} | "
        md += f"**Phone:** {tailored_resume_data['personal_info']['phone']} | "
        md += f"**LinkedIn:** {tailored_resume_data['personal_info']['linkedin']} | "
        md += f"**GitHub:** {tailored_resume_data['personal_info']['github']}\n\n"

        md += "## Education\n"
        for edu in tailored_resume_data["education"]:
            md += f"- **{edu['degree']}** in {edu['major']}\n"
            md += f"  - {edu['institution']}, {edu['location']} ({edu['start_date']} - {edu['end_date']})\n"
            if edu.get("gpa"): md += f"  - GPA: {edu['gpa']}\n"
            if edu.get("honors"): md += f"  - Honors: {edu['honors']}\n"
        md += "\n"

        md += "## Work Experience\n"
        for exp in tailored_resume_data["work_experience"]:
            md += f"### {exp['title']} at {exp['company']}\n"
            md += f"**{exp['location']}** | {exp['start_date']} - {exp.get('end_date', 'Present')}\n"
            for desc_line in exp.get("description", []):
                md += f"- {desc_line}\n"
            if exp.get("technologies"):
                md += f"- **Technologies:** {', '.join(exp['technologies'])}\n"
            md += "\n"

        md += "## Projects\n"
        for proj in tailored_resume_data["projects"]:
            md += f"### {proj['name']}\n"
            md += f"**{proj['start_date']}** - {proj.get('end_date', 'Present')}\n"
            for desc_line in proj.get("description", []):
                md += f"- {desc_line}\n"
            if proj.get("technologies"):
                md += f"- **Technologies:** {', '.join(proj['technologies'])}\n"
            if proj.get("link"):
                md += f"- **Link:** {proj['link']}\n"
            md += "\n"

        md += "## Skills\n"
        for category, skills_list in tailored_resume_data["skills"].items():
            if skills_list:
                md += f"**{category}:** {', '.join(skills_list)}\n"
        md += "\n"

        return md
