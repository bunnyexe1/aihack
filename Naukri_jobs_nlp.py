import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import spacy
import time
import logging
from typing import List, Tuple

# Configure logging
logging.basicConfig(filename='scraper.log', level=logging.INFO)

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Function to extract additional information using NLP
def extract_info(text: str) -> Tuple[List[str], List[str], List[str]]:
    """
    Extract skills, locations, and experience from text using spaCy.
    """
    doc = nlp(text)
    skills = [ent.text for ent in doc.ents if ent.label_ in ["SKILL", "ORG"]]
    locations = [ent.text for ent in doc.ents if ent.label_ == "GPE"]
    experience = [ent.text for ent in doc.ents if ent.label_ == "DATE"]
    return skills, locations, experience

# Function to scrape job listings
def scrape_jobs(skill: str) -> List[dict]:
    """
    Scrape job listings from Naukri.com for a given skill.
    """
    # Set up Chrome WebDriver
    driver_path = r"C:\Users\kmohi\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe"  # Update this path
    service = Service(driver_path)
    web = webdriver.Chrome(service=service)

    jobs = []
    try:
        # Construct the URL
        url = f"https://www.naukri.com/{skill}-jobs?k={skill}"
        st.write(f"Scraping jobs for skill: **{skill}**")
        st.write(f"URL: {url}")

        # Open the URL
        web.get(url)

        # Wait for the page to load
        WebDriverWait(web, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "cust-job-tuple")))

        # Parse the page
        html = web.page_source
        soup = BeautifulSoup(html, 'html.parser')

        # Find all job cards
        job_cards = soup.find_all("div", {"class": "cust-job-tuple"})

        # Extract job details
        for job in job_cards:
            title = job.find("a", {"class": "title"})
            company = job.find("a", {"class": "comp-name"})
            experience = job.find("span", {"class": "expwdth"})
            salary = job.find("span", {"class": "sal"})
            location = job.find("span", {"class": "locWdth"})
            skills_list = job.find_all("li", {"class": "tag-li"})
            description = job.find("span", {"class": "job-desc"})

            # Extract additional info using NLP
            if description:
                skills_nlp, locations_nlp, experience_nlp = extract_info(description.text.strip())
            else:
                skills_nlp, locations_nlp, experience_nlp = [], [], []

            # Store job details
            jobs.append({
                "title": title.text.strip() if title else "N/A",
                "company": company.text.strip() if company else "N/A",
                "experience": experience.text.strip() if experience else "N/A",
                "salary": salary.text.strip() if salary else "N/A",
                "location": location.text.strip() if location else "N/A",
                "skills_explicit": [skill.text.strip() for skill in skills_list] if skills_list else [],
                "url": title.get("href") if title else "N/A"
            })

    except Exception as e:
        logging.error(f"Error scraping jobs: {e}")
        st.error(f"Error scraping jobs: {e}")

    finally:
        # Close the browser
        web.quit()

    return jobs

# Streamlit UI
st.title("JobInsight: AI-Powered Job Search and Analysis Tool")
st.write("Enter a skill to search for jobs on Naukri.com")

# Input skill from the user
skill = st.text_input("Enter your prompt")

# Scrape and display jobs when the user clicks the button
if st.button("Search Jobs"):
    if skill:
        with st.spinner("Scraping jobs..."):
            jobs = scrape_jobs(skill)
            if jobs:
                st.success(f"Found {len(jobs)} jobs!")
                for job in jobs:
                    st.write("---")
                    st.write(f"**Job Title:** {job['title']}")
                    st.write(f"**Company:** {job['company']}")
                    st.write(f"**Experience:** {job['experience']}")
                    st.write(f"**Salary:** {job['salary']}")
                    st.write(f"**Location:** {job['location']}")
                    st.write(f"**Skills (Explicit):** {job['skills_explicit']}")
                    st.write(f"**URL:** {job['url']}")
            else:
                st.warning("No jobs found for the given skill.")
    else:
        st.warning("Please enter a skill to search for jobs.")