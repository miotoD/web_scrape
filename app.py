from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import csv


#type .\env\Scripts\activate.ps1 to activate and run the environment 
# after that type python 'filename.py' to run the script in windows , and source myenv/bin/activate on MAC

# Setting up Chrome options for headless mode
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")  # Enable headless mode
chrome_options.add_argument("--disable-dev-shm-usage")  
chrome_options.add_argument("--disable-gpu")

# Initializing webdriver
driver = webdriver.Chrome(options=chrome_options)


#first website to target
website = "https://supremecourt.gov.np/lic/sys.php?d=reports&f=case_details"
driver.get(website)

#second webiste to target
home_page = "https://supremecourt.gov.np/web/index.php/index"

# Waiting for the input field element to be present in the webpage
reg_no_field = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, "//input[@id='regno']"))
)

reg_no = input("Please enter the regno of the case here: ") # from terminal

# send the regno into the input field
reg_no_field.send_keys(reg_no)

# Locate and click the submit button
submit_button = driver.find_element(By.XPATH, "//input[@type='submit' and @value='    खोज्ने     ']")
submit_button.click()

# Handling if no records found
try:
    checking_records = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//strong[text()='Total 0 Records Found']"))
    )
    print("No such records found!")
except TimeoutException:
    print("Record found!")

# Handling result loading and scraping the table
try:
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//table"))
    )

    table = driver.find_element(By.XPATH, "//table")
    rows = table.find_elements(By.TAG_NAME, "tr")
    columns = table.find_elements(By.TAG_NAME, "td")

    print("--------------------------")

except TimeoutException:
    print("No results found")

# Locating and clicking the case details link  
link = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, "//a[contains(text(),'मुद्दाको बिस्तृत विवरण')]"))
)
link.click()

#after clicking, goes to the new url / page refreshes
# wait for the new page content to load
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, "//td[contains(text(),'दर्ता नँ')]"))
)

# Re-fetch table elements after page navigation
try:
    new_table = driver.find_element(By.XPATH, "//table")
    new_rows = new_table.find_elements(By.TAG_NAME, "tr")
    
    empty_rows = driver.find_element(By.XPATH, "//td[@colspan='3']/font[@size='2' and @color='#000000']")
    
    # Iterate through the new rows and print the data
    for row in new_rows:
        new_cols = row.find_elements(By.TAG_NAME, "td")
        for col in new_cols:
            if col.text.strip() == "":
                print("NULL")
            else:
                print(col.text)

except TimeoutException:
    print("New table not found on the case detail page.")


#navigating to the homepage to fetch new data
driver.get(home_page)

print("----------------------------------------------------------------------")
print("Now we are on the home page.")

#finding the specifi element in the homepage
try:
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//tbody"))
    )
    tbody = driver.find_element(By.XPATH, "//tbody")
    
    rows = tbody.find_elements(By.TAG_NAME, "tr")

    for row in rows:
        case_numbers = row.find_elements(By.TAG_NAME, "td")
        caseStatus = row.find_elements(By.TAG_NAME, "th")
        
        for numbers, status in zip(case_numbers, caseStatus):
            print(f"{status.text},{numbers.text}")

    # CSV file for writing scraped data 
    with open("case_status.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Case Status", "Case Numbers"])  #Headers for datas respectively
        for row in rows:
            case_numbers = row.find_elements(By.TAG_NAME, "td")
            caseStatus = row.find_elements(By.TAG_NAME, "th")
            for numbers, status in zip(case_numbers, caseStatus):
                writer.writerow([status.text, numbers.text])

except TimeoutException:
    print("Timed out")

# Close the browser
driver.quit()
