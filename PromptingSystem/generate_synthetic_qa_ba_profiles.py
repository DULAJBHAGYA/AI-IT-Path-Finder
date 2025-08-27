import json
import random
from faker import Faker

fake = Faker()


def random_skills(role):
    if role == "Business Analyst":
        return [
            {"category": "Business Analysis", "items": ["Requirements Gathering", "Process Mapping", "Stakeholder Management"]},
            {"category": "Tools", "items": ["JIRA", "Confluence", "MS Visio"]}
        ]
    else:
        return [
            {"category": "Testing", "items": ["Manual Testing", "Automation Testing", "Regression Testing"]},
            {"category": "Tools", "items": ["Selenium", "JMeter", "Postman"]}
        ]

def random_experience(role):
    if role == "Business Analyst":
        return [
            {
                "title": "Business Analyst",
                "company": fake.company(),
                "duration": f"{random.randint(2015, 2022)} - {random.randint(2023, 2025)}",
                "responsibilities": [
                    "Gathered and analyzed business requirements.",
                    "Facilitated communication between stakeholders and technical teams.",
                    "Created process maps and documentation."
                ]
            }
        ]
    else:
        return [
            {
                "title": "QA Engineer",
                "company": fake.company(),
                "duration": f"{random.randint(2015, 2022)} - {random.randint(2023, 2025)}",
                "responsibilities": [
                    "Designed and executed test cases.",
                    "Automated regression tests using Selenium.",
                    "Reported and tracked bugs in JIRA."
                ]
            }
        ]

def random_projects(role):
    if role == "Business Analyst":
        return [
            {
                "name": "Process Improvement Initiative",
                "role": "Lead Analyst",
                "description": "Led a project to improve business processes and reduce costs.",
                "technologies": ["MS Visio", "Excel"]
            }
        ]
    else:
        return [
            {
                "name": "Test Automation Framework",
                "role": "QA Lead",
                "description": "Developed a Selenium-based automation framework.",
                "technologies": ["Selenium", "Python"]
            }
        ]

def random_education():
    return [
        {
            "degree": "B.Sc. in Computer Science",
            "institution": fake.company() + " University",
            "duration": f"{random.randint(2010, 2014)} - {random.randint(2015, 2018)}",
            "details": "Graduated with honors."
        }
    ]

def random_references():
    return [
        {
            "name": fake.name(),
            "title": "Manager",
            "phone": fake.phone_number(),
            "email": fake.email()
        }
    ]

def random_profile(role):
    return {
        "name": fake.name(),
        "job_title": role,
        "contact": {
            "email": fake.email(),
            "phone": fake.phone_number(),
            "location": fake.city() + ", " + fake.country(),
            "linkedin": f"linkedin.com/in/{fake.user_name()}",
            "github": f"github.com/{fake.user_name()}",
            "website": fake.url()
        },
        "profile_summary": fake.text(max_nb_chars=150),
        "skills": random_skills(role),
        "experience": random_experience(role),
        "projects": random_projects(role),
        "education": random_education(),
        "volunteering_and_leadership": [fake.sentence(nb_words=8)],
        "references": random_references()
    }

# Generate 1,000 profiles (500 QA, 500 BA)
profiles = []
for _ in range(500):
    profiles.append(random_profile("Business Analyst"))
for _ in range(500):
    profiles.append(random_profile("QA Engineer"))

# Save to JSON
with open("synthetic_qa_ba_profiles.json", "w", encoding="utf-8") as f:
    json.dump(profiles, f, indent=2)

print("Generated 1,000 synthetic QA/BA profiles in synthetic_qa_ba_profiles.json") 