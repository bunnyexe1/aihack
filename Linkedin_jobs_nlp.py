import streamlit as st
import json
import subprocess
import spacy
import google.generativeai as genai
import json
import re
# from google import genai
# Load spaCy model
nlp = spacy.load("en_core_web_sm")
entities = {
        "keyword": None,
        "location": None,
        "date_since_posted": None,
        "job_type": None,
        "remote_filter": None,
        "salary": None,
        "experience_level": None,
        "limit": 20,
        "page": 0,
    }

genai.configure(api_key="AIzaSyA3dqyqPY626oDCBJi8U3y3WdjX8MSAQZI")
def extract_entities_with_gemini(prompt):

    # Define the system instruction to extract structured data
    instruction= """Extract job details from the given user query. 
    Return a structured JSON with the following fields:
    - keyword (Job title)
    - location (City or Country)
    - date_since_posted (One of: 'past Day', 'past Week', 'past Month')
    - job_type (One of: 'full time', 'part time', 'contract', 'temporary', 'internship')
    - remote_filter (One of: 'on-site', 'remote', 'hybrid')
    - salary (Minimum salary as an integer)
    - experience_level (One of: 'entry level', 'associate', 'mid-senior', 'director', 'executive')
    - limit (Integer, number of results)
    - page (Integer, page number)

    If any field is missing in the user's query, use the default values:
    - keyword: "software engineer"
    - location: "Hyderabad"
    - date_since_posted: "past Month"
    - job_type: "full time"
    - remote_filter: "on-site"
    - salary: 100000
    - experience_level: "mid-senior"
    - limit: 20
    - page: 0

    Example Query: "Find remote software engineer jobs in New York with a salary of $120,000"
    Example Output:
    {
        "keyword": "software engineer",
        "location": "New York",
        "date_since_posted": "past Month",
        "job_type": "full time",
        "remote_filter": "remote",
        "salary": 120000,
        "experience_level": "mid-senior",
        "limit": 20,
        "page": 0
    }
    """

    #Call Gemini API
    

    
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(f"{instruction}\nUser Query: {prompt}")
    response_text = response.text.strip()
    json_start = response_text.find("{")
    json_end = response_text.rfind("}") + 1

    if json_start != -1 and json_end != -1:
        response_text = response_text[json_start:json_end]
    print(response_text)
    extracted_data=json.loads(response_text)
    print(extracted_data)
    return extracted_data



def extract_entities(prompt):
    doc = nlp(prompt)

    # Default values
    entities = {
        "keyword": None,
        "location": None,
        "date_since_posted": None,
        "job_type": None,
        "remote_filter": None,
        "salary": None,
        "experience_level": None,
        "limit": 20,
        "page": 0,
    }

    # Extracting Named Entities
    for ent in doc.ents:
        if ent.label_ == "GPE":  # Location
            entities["location"] = ent.text
        elif ent.label_ == "DATE":
            entities["date_since_posted"] = ent.text
        elif ent.label_ == "MONEY":
            try:
                entities["salary"] = int(re.sub(r"[^\d]", "", ent.text))  # Extract numeric salary
            except ValueError:
                entities["salary"] = None

    # **Extract Job Title (Keyword) Using Regex & Heuristics**
    job_title_pattern = re.findall(r"(?:for|as|to be|hiring a|looking for a)\s+([a-zA-Z\s]+?)(?:\sin|with|at|,|$)", prompt, re.IGNORECASE)
    if job_title_pattern:
        entities["keyword"] = job_title_pattern[0].strip()
    else:
        # Fallback: Check for common job-related words in the prompt
        words = prompt.lower().split()
        job_titles = ["software engineer", "data scientist", "project manager", "business analyst", "devops engineer"]
        for title in job_titles:
            if title in prompt.lower():
                entities["keyword"] = title
                break

    # Extracting job-related details using keyword matching
    job_types = ["full time", "part time", "contract", "temporary", "internship"]
    for job in job_types:
        if job in prompt.lower():
            entities["job_type"] = job
            break  

    experience_levels = ["entry level", "associate", "mid-senior", "director", "executive"]
    for level in experience_levels:
        if level in prompt.lower():
            entities["experience_level"] = level
            break

    if "remote" in prompt.lower():
        entities["remote_filter"] = "remote"
    elif "hybrid" in prompt.lower():
        entities["remote_filter"] = "hybrid"
    elif "on-site" in prompt.lower():
        entities["remote_filter"] = "on-site"

    # Set defaults if values are still None
    if entities["keyword"] is None:
        entities["keyword"] = "software engineer"  # Default job title
    if entities["location"] is None:
        entities["location"] = "Hyderabad"  
    if entities["date_since_posted"] is None:
        entities["date_since_posted"] = "past Month"
    if entities["job_type"] is None:
        entities["job_type"] = "full time"
    if entities["remote_filter"] is None:
        entities["remote_filter"] = "on-site"
    if entities["salary"] is None:
        entities["salary"] = 100000
    if entities["experience_level"] is None:
        entities["experience_level"] = "mid-senior"

    return entities



# Function to create a job card
def create_job_card(job):
    with st.container():
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"### {job['position']}")
            st.markdown(f"Company: {job['company']}")
            st.markdown(f"Location: {job['location']}")
            st.markdown(f"Date Posted: {job['date']}")
            st.markdown(f"Salary: {job['salary']}")
            st.markdown(f"Job URL: [Apply Here]({job['jobUrl']})")
            st.markdown(f"Posted: {job['agoTime']}")
        
        with col2:
            st.image(job['companyLogo'], width=150)
        
        st.markdown("---")

# Function to filter out duplicate jobs
def filter_unique_jobs(jobs):
    unique_jobs = []
    seen = set()  # Track unique job identifiers

    for job in jobs:
        # Create a unique identifier for the job (e.g., combination of position, company, and job URL)
        job_identifier = (job['position'], job['company'], job['jobUrl'])

        if job_identifier not in seen:
            seen.add(job_identifier)
            unique_jobs.append(job)

    return unique_jobs

# Streamlit UI
st.title("Jobs Search")

# Main search by prompt
st.header("Search by Prompt")
prompt = st.text_input("Enter your job search prompt (e.g., 'Find remote software engineer jobs in New York with a salary of $100,000')")



if st.button("Search Jobs"):
    if prompt:
    # Extract entities from the prompt
        entities = extract_entities_with_gemini(prompt)
    else:
        entities = {}  # Ensure `entities` is always a dictionary to prevent KeyErrors

    # Advanced options (collapsible)
    with st.expander("Advanced Options"):
        st.header("Search Filters")
        keyword = st.text_input("Keyword", entities.get("keyword", "Software engineer"))
        location = st.text_input("Location", entities.get("location", "India"))
        date_since_posted = st.selectbox(
            "Date Since Posted", ["past Day", "past Week", "past Month"],
            index=["past Day", "past Week", "past Month"].index(entities.get("date_since_posted", "past Week"))
        )
        job_type = st.selectbox(
            "Job Type", ["full time", "part time", "contract", "temporary", "internship"],
            index=["full time", "part time", "contract", "temporary", "internship"].index(entities.get("job_type", "full time"))
        )
        remote_filter = st.selectbox(
            "Remote Filter", ["on-site", "remote", "hybrid"],
            index=["on-site", "remote", "hybrid"].index(entities.get("remote_filter", "on-site"))
        )
        salary = st.number_input("Minimum Salary", min_value=0, step=1000, value=int(entities.get("salary", 100000)))
        experience_level = st.selectbox(
            "Experience Level", ["entry level", "associate", "mid-senior", "director", "executive"],
            index=["entry level", "associate", "mid-senior", "director", "executive"].index(entities.get("experience_level", "mid-senior"))
        )
        limit = st.slider("Number of Results", 1, 50, int(entities.get("limit", 20)))
        page = st.number_input("Page Number", min_value=0, step=1, value=int(entities.get("page", 0)))

    # Construct query_options (same for both cases)
    query_options = {
        "keyword": keyword,
        "location": location,
        "dateSincePosted": date_since_posted,
        "jobType": job_type,
        "remoteFilter": remote_filter,
        "salary": str(salary),
        "experienceLevel": experience_level,
        "limit": str(limit),
        "page": str(page),
    }

    print(query_options)
    with open("query_options.json", "w") as f:
        json.dump(query_options, f)
    
    subprocess.run(['node', 'api.js'])
    
    with open('jobs_data.json', 'r') as file:
        try:
            jobs = json.load(file)
            st.success("Jobs fetched successfully!")

            # Filter out duplicate jobs
            unique_jobs = filter_unique_jobs(jobs)

            # Display the number of unique jobs found
            st.write(f"Found {len(unique_jobs)} jobs for you.")

            # Display each unique job
            for job in unique_jobs:
                create_job_card(job)
        except json.JSONDecodeError:
            st.error("Invalid JSON returned from the Node.js script. Raw output:")
            st.text(file.read())