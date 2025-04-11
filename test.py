from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

def get_linkedin_job_description(job_url):
    # Set up Selenium WebDriver
    options = Options()
    options.add_argument("--headless")  # Run in headless mode (no UI)
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        driver.get(job_url)
        time.sleep(5)  # Wait for the page to load completely
        
        # Locate core-rail section inside the main content
        main_section = driver.find_element(By.TAG_NAME, "main")
        core_rail = main_section.find_element(By.CLASS_NAME, "core-rail")
        
        # Find and click the button with id containing 'ember' inside core-rail
        button = None
        for btn in core_rail.find_elements(By.TAG_NAME, "button"):
            if "ember" in btn.get_attribute("id"):
                button = btn
                break
        
        if button:
            button.click()
            time.sleep(2)  # Wait for content to load
        
        # Find div with class 'jobs-description-content__text--stretch'
        job_description_div = core_rail.find_element(By.ID, "jobs-details")
        job_description_text = job_description_div.text.strip()
        
        return job_description_text
    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        driver.quit()

if __name__ == "__main__":
    job_url = "https://www.linkedin.com/jobs/view/software-engineer-lead-java-remote-at-us-foods-4131373856?position=1&pageNum=0&refId=rWJ82MLx4GCBR%2FJ4A35S1Q%3D%3D&trackingId=R6Idcv62itDarLuhcEPZwg%3D%3D"  # Replace with the actual LinkedIn job URL
    description = get_linkedin_job_description(job_url)
    if description:
        print("Job Description:\n", description)
    else:
        print("Failed to extract job description.")
