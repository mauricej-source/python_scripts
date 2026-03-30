import setuptools 
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time
import pandas as pd
import os

def calculate_score(jd_text, must_haves, optionals):
    found_must = [word for word in must_haves if word.lower() in jd_text]
    if len(found_must) < len(must_haves):
        return False, 0, []

    found_optional = [word for word in optionals if word.lower() in jd_text]
    score = (len(found_optional) / len(optionals)) * 100 if optionals else 100
    return True, score, found_optional

def global_hunter(job_titles, location, must_haves, optionals):
    driver = None
    all_matches = []
    seen_job_ids = set() 
    
    try:
        options = uc.ChromeOptions()
        driver = uc.Chrome(options=options)
        if not driver: return
        
        base_url = "https://www.indeed.com"

        for title in job_titles:
            print(f"\n[SEARCHING] Targeting Title: {title}...")
            #search_url = f"{base_url}/jobs?q={title.replace(' ', '+')}&l={location.replace(' ', '+')}"
            
            search_url = f"https://www.indeed.com/jobs?q={title.replace(' ', '+')}&latLong=30.34890%2C-81.50107&locString=Jacksonville%2C+FL%2C+32225&radius=50&from=searchOnDesktopSerp%2Cwhatautocomplete%2CwhatautocompleteSourceStandard%2Cwhereautocomplete"
            
            driver.get(search_url)
            time.sleep(7) 

            cards = driver.find_elements(By.CLASS_NAME, 'resultContent')
            
            for card in cards:
                try:
                    # Deduplication Logic
                    link_element = card.find_element(By.CSS_SELECTOR, 'h2.jobTitle a')
                    job_url = link_element.get_attribute('href')
                    job_id = job_url.split('jk=')[-1].split('&')[0] if 'jk=' in job_url else job_url

                    if job_id in seen_job_ids:
                        continue
                    seen_job_ids.add(job_id)

                    # Click and Scrape
                    card.click()
                    time.sleep(3) # Increased slightly for reliability

                    jd_text = ""
                    for sel in ['#jobDescriptionText', '.jobsearch-JobComponent-description']:
                        els = driver.find_elements(By.CSS_SELECTOR, sel)
                        if els:
                            jd_text = els[0].text.lower()
                            break

                    is_match, score, bonus_found = calculate_score(jd_text, must_haves, optionals)

                    if is_match:
                        job_title_text = card.find_element(By.CSS_SELECTOR, 'h2.jobTitle').text
                        company = card.find_element(By.CSS_SELECTOR, '[data-testid="company-name"]').text
                        
                        # Formatting for Excel
                        all_matches.append({
                            'Company': company,
                            'Job Title': job_title_text,
                            'Percent Match': f"{score:.1f}%",
                            'Job Link': job_url if job_url.startswith('http') else base_url + job_url
                        })
                        print(f"   ✨ Added to list: {job_title_text} at {company}")

                except Exception:
                    continue

    except Exception as e:
        print(f"[ERROR] Session error: {e}")

    finally:
        if driver:
            print("\n[SYSTEM] Shutting down stealth driver...")
            try:
                driver.quit()
            except:
                pass
            driver = None

        # --- EXCEL EXPORT LOGIC ---
        if all_matches:
            # Create DataFrame
            df = pd.DataFrame(all_matches)
            
            # Reorder columns as requested
            df = df[['Company', 'Job Title', 'Percent Match', 'Job Link']]
            
            # Save to current directory
            filename = "indeed_global_job_search.xlsx"
            df.to_excel(filename, index=False)
            
            full_path = os.path.abspath(filename)
            print("\n" + "="*50)
            print(f"✅ SUCCESS! Data saved to Excel.")
            print(f"📂 PATH: {full_path}")
            print(f"📊 TOTAL JOBS FOUND: {len(all_matches)}")
            print("="*50)
        else:
            print("\n[SYSTEM] No matches found. No Excel file created.")

# -- ------------------------------------------------------------------------------------- --
# --                                  Configuration                                        --
# -- ------------------------------------------------------------------------------------- --
target_job_titles = ["Platform Engineer", "Site Reliability Engineer", "Release Engineer", "Cloud Architect", "Cloud Platform", "Software Engineer", "Java Engineer", "Java Developer", "Backend Engineer"]

must_have_keywords = ["Java"]

additional_optional_keywords = ["AWS", "SQL"
    "Python", "EKS", "K8", "Kubernete", "EC2", "Azure", 
    "Terraform", "Jenkins", "Groovy", "Splunk", "New Relic", "Dynatrace",
	"DEVOPS", "DevOps", "CICD"
]

must_not_have_keywords = ["React", "Angular", "Vue", "Javascript", "JavaScript", ".Net", ".NET"]

global_hunter(target_job_titles, "Remote", must_have_keywords, additional_optional_keywords)