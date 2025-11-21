from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import time
import os
import csv
import shutil
import logging
import pickle

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define the simplified_html function
def simplified_html(html_content: str, filename: str) -> str:
    try:
        soup = BeautifulSoup(html_content, "html.parser")
        
        result = {
            "guidelines": "",
            "article_info": "",
            "author_info": "",
            "problem_notes": "",
            "comments": "",
            "Attachments": ""
        }

        # ------------------ GUIDELINES ------------------
        sections = ["Style"]    
        for section in sections:    
            style_legend = soup.find('legend', string='Style')
            if style_legend:
                style_fieldset = style_legend.find_parent('fieldset', class_='FormFieldset')
                if style_fieldset:
                    for row in style_fieldset.find_all('tr'):
                        cells = row.find_all('td')
                        if len(cells) >= 2 and section in cells[0].text.strip():
                            textarea = cells[1].find('textarea')
                            if textarea:
                                content = textarea.text.strip()
                                num_lines = len(content.split('\n'))
                                textarea.attrs['rows'] = str(num_lines + 5)  
                                textarea['style'] = (
                                    'overflow: hidden; resize: none; width: 100%; '
                                    'min-height: auto; max-width: 100%; box-sizing: border-box; '
                                    'white-space: pre-wrap; word-wrap: break-word; height: auto;'
                                )
                    result['guidelines'] += f"""
                    <div class="box" style="display: block; width: auto; min-width: 100%; max-width: 100%; white-space: pre-wrap;">
                         <div class="header">Article Guidelines</div>
                         {str(style_fieldset)}
                    </div>
                    """            

        # ------------------ ARTICLE INFO ------------------
        article_info_div = soup.find("div", id="ArticleInfo")
        if article_info_div:
            for select in article_info_div.find_all('select'):
                select.decompose()
            for link in article_info_div.find_all('a', string='Open the calendar popup.'):
                parent_td = link.find_parent('td')
                if parent_td:
                    date_input = parent_td.find('input', type='text')
                    if date_input:
                        new_input = soup.new_tag('input', type='date')
                        new_input['value'] = date_input.get('value', '')
                        new_input['class'] = 'date-input'
                        parent_td.clear()
                        parent_td.append(new_input)
            for checkbox in soup.find_all("input", {"type": "checkbox"}):
                checkbox.attrs["class"] = "readonly"
            for link in article_info_div.find_all("a"):
                link.decompose()

            result['article_info'] += f"""
            <html>
            <head>
            <style>
            .articlebox {{ border: 1px solid #ccc; padding: 15px; margin: 10px; background: white; height: 220%; }}
            </style>
            </head>
            <body>
            <div class="articlebox">
                <div class="header">Article Information_{article['jid']}{article['aid']}</div>
                <div class="rmpView" id="ArticleInfo">
                    {str(article_info_div)}
                </div>
            </div>
            """

        # ------------------ AUTHOR INFO ------------------
        author_info_div = soup.find("div", id="ctl00_ArticleAuthors_uc_ArticleAuthorsGrid")
        if author_info_div:
            for select in author_info_div.find_all('select'):
                select.decompose()
            for link in author_info_div.find_all("a"):
                span_tag = soup.new_tag("span")
                span_tag.string = link.text
                link.replace_with(span_tag)
            for checkbox in soup.find_all("input", {"type": "checkbox"}):
                checkbox.attrs["class"] = "readonly"   
            for img in author_info_div.find_all("img"):
                img.decompose()
            for input_img in author_info_div.find_all('input', type='image'):
                span_tag = soup.new_tag("span")
                span_tag.string = "Submit"
                input_img.replace_with(span_tag)

            structured_table = f"""
            <table class="structured-table">
                <tbody>
                    <tr>
                        <td>{str(author_info_div)}</td>
                    </tr>
                </tbody>
            </table>
            """         

            result['author_info'] += f"""
            <div class="box">
                <div class="header">Author Information</div>
                <div class="rmpView" id="AuthorInfo">
                    {structured_table}
                </div>
            </div>
            """

        # ------------------ PROBLEM NOTES ------------------
        problem_notes_div = soup.find("div",id="ArticleProbNotes")  # ✅ adjust actual ID
        if problem_notes_div:
            for select in problem_notes_div.find_all('select'):
                select.decompose()
            for link in problem_notes_div.find_all("a"):
                span_tag = soup.new_tag("span")
                span_tag.string = link.text
                link.replace_with(span_tag)   
            result['problem_notes'] += f"""
            <div class="articlebox" id="ProblemNotes">
                <div class="header">Problem Notes – {article['jid']}{article['aid']}</div>
                <div class="rmpView">
                    {str(problem_notes_div)}
                </div>
            </div>
            """
        # ------------------ Comments_tab------------------
        comments_tab = soup.find("div",id="ArticleComments")
        if comments_tab:
            for select in comments_tab.find_all('select'):
                select.decompose()
            for link in comments_tab.find_all('a'):
                span_tag=soup.new_tag("span")
                span_tag.string = link.text
                link.replace_with(span_tag)
            for checkbox in soup.find_all("input", {"type": "checkbox"}):
                checkbox.attrs["class"] = "readonly"
            for img in comments_tab.find_all("img"):
                img.decompose()
            for input_img in comments_tab.find_all('input', type='image'):
                span_tag = soup.new_tag("span")
                span_tag.string = "Submit"
                input_img.replace_with(span_tag)            
            result['comments'] += f"""
            <div class="articlebox" id="CommentsInfo">
                <div class="header">Comments – {article['jid']}{article['aid']}</div>
                <div class="rmpView">
                    {str(comments_tab)}
                </div>
            </div>
            """

        attachments_tab = soup.find("div",id="ArticleAttachmentGrid")
        if attachments_tab:
            for select in attachments_tab.find_all('select'):
                select.decompose()
            for link in attachments_tab.find_all('a'):
                span_tag=soup.new_tag("span")
                span_tag.string = link.text
                link.replace_with(span_tag)
            for checkbox in soup.find_all("input", {"type": "checkbox"}):
                checkbox.attrs["class"] = "readonly"
            for img in attachments_tab.find_all("img"):
                img.decompose()
            for input_img in attachments_tab.find_all('input', type='image'):
                span_tag = soup.new_tag("span")
                span_tag.string = "Submit"
                input_img.replace_with(span_tag)            
            result['Attachments'] += f"""
            <div class="articlebox" id="CommentsInfo">
                <div class="header">Attachments – {article['jid']}{article['aid']}</div>
                <div class="rmpView">
                    {str(attachments_tab)}
                </div>
            </div>
            """                 

        if not result['author_info']:
            logging.warning(f"No relevant content found in: {filename}")

        return result  # ✅

    except Exception as e:
        logging.error(f"Error processing HTML content for {filename}: {str(e)}")
        return f"<html><body><h3>Error processing HTML: {str(e)}</h3></body></html>"


def clean_previous_article_data(downloads_dir, jid, aid):
    article_id = f"{jid}{aid}".lower()
    article_path = os.path.join(downloads_dir, article_id)
    merged_file = os.path.join(article_path, f"{article_id}_merged.html")

    if os.path.exists(merged_file):
        print(f"🧹 Skipping already processed article: {article_id}")
        shutil.rmtree(article_path)
        return False
    return True

def merge_simplified_html(article_id: str, article: dict,full_html_content:dict, download_dir: str):
    """
    Merges extracted HTML sections into a final merged HTML file and saves it.
    """
    # extracted = simplified_html(full_html_content, article)
    extracted = full_html_content
    merged_html = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            html , body {{ margin: 0; padding: 0; width: 100%; height: 100%;  }}
            .box {{  border: 1px solid #ccc; padding: 15px; margin: 10px; background: white; height: auto; }}
            .header {{ font-size: 40px; font-weight: bold; margin-bottom: 10px; }}
            .StandardTable {{width: 100%; border-collapse: collapse; background: white; border: 1px solid #ddd;}}
            .StandardTable td {{padding: 8px; border: 1px solid #ddd; vertical-align: top;}}
            textarea, input[type="text"], input[type="date"], select {{ width: 100%; padding: 5px; box-sizing: border-box; border: 1px solid #ccc; background-color: #fff;}}
            #ctl00_ArticleInfo_uc_dtpsubdt_dateInput,
            #ctl00_ArticleInfo_uc_dtpRevisedSubmissionDate_dateInput,
          /* Step 1: Target wrapper spans of the date inputs */
            #ctl00_ArticleInfo_uc_dtpsubdt_dateInput_wrapper,
            #ctl00_ArticleInfo_uc_dtpRevisedSubmissionDate_dateInput_wrapper,
            #ctl00_ArticleInfo_uc_dtpacceptdt_dateInput_wrapper {{
                width: 200px !important;
                display: block !important;
            }}

            /* Step 2: Target the actual input fields inside them */
            #ctl00_ArticleInfo_uc_dtpsubdt_dateInput,
            #ctl00_ArticleInfo_uc_dtpRevisedSubmissionDate_dateInput,
            #ctl00_ArticleInfo_uc_dtpacceptdt_dateInput {{
                width: 70% !important;
                padding: 6px;
                box-sizing: border-box;
                font-size: 13px;
            }}
            input[readonly], textarea[readonly] {{
            background-color: #e9ecef;
            cursor: text;
            }}
            input[type="checkbox"]:disabled:checked {{accent-color: #1cbc1c; filter: brightness(0);}}
            .structured-table {{width: 100%; border-collapse: collapse; margin-top: 10px; table-layout:auto; }}
            .structured-table th, .structured-table td {{padding: 10px; border: 1px solid #ddd; text-align: left; white-space:normal;}}
            .structured-table {{ background-color: #f2f2f2; font-weight: bold;}}
            .structured-table th {{ background-color: #f2f2f2; }}
            .structured-table th {{background-color: #f2f2f2; font-weight: bold; }}
            .structured-table tr:nth-child(even) {{ background-color: #f9f9f9;}}
            .footer-section {{margin-top: 20px; padding: 15px; text-align: left; font-size: 18px;}}
            .footer-section a {{ text-decoration: none; font-size: 18px; color: blue;}}
            .footer-section .bold-link {{ font-weight: bold; }}
            @media (max-width: 768px) {{
                .header {{ font-size: 2rem; }}
                .box {{padding: 10px; margin: 5px; }}
                textarea, input[type="text"], input[type="date"], select {{ width: 100%; }}
                .footer-section {{font-size: 1rem; padding: 10px; }}
                .footer-section a {{ font-size: 1rem;}}
            }}
            @media (max-width: 480px) {{
                .header {{font-size: 1.5rem;}}
                .box {{padding: 5px; margin: 3px;}}
                .footer-section {{font-size: 0.875rem; padding: 5px;}}
                .footer-section a {{font-size: 0.875rem;}}
            }}
            #AuthorInfo, .box, .rmpView{{overflow:visible;height:auto;max-height:none;display:block;}}
            #AuthorInfo .header {{font-size: 48px;}} /* Increase header font size */
            #AuthorInfo .structured-table th, 
            #AuthorInfo .structured-table td {{font-size: 12px;}} /* Increase table font size */
            #AuthorInfo .structured-table{{width:100%;max-width:100%;}}
            input, textarea {{ pointer-events: none; background-color: #e9ecef; }}
            input[type="checkbox"].readonly {{ accent-color: #1923e3;}}
            <style>
            /* ---------------- Problem Notes Section ---------------- */
            #ProblemNotes {{
                overflow: visible;
                height: auto;
                max-height: none;
                display: block;
            }}
            #ProblemNotes .header {{
                font-size: 28px;
                font-weight: bold;
                margin-bottom: 12px;
                color: #2a2a7f; /* dark blue for distinction */
            }}
            #ProblemNotes table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 10px;
            }}
            #ProblemNotes th, 
            #ProblemNotes td {{
                border: 1px solid #ccc;
                padding: 8px;
                text-align: left;
                font-size: 13px;
            }}
            #ProblemNotes tr:nth-child(even) {{
                background-color: #f9f9f9;
            }}

            /* ---------------- Comments Section ---------------- */
            #CommentsInfo {{
                overflow: visible;
                height: auto;
                max-height: none;
                display: block;
            }}
            #CommentsInfo .header {{
                font-size: 28px;
                font-weight: bold;
                margin-bottom: 12px;
                color: #1a6b1a; /* dark green for distinction */
            }}
            #CommentsInfo table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 10px;
            }}
            #CommentsInfo th, 
            #CommentsInfo td {{
                border: 1px solid #ccc;
                padding: 8px;
                text-align: left;
                font-size: 13px;
                vertical-align: top;
            }}
            #CommentsInfo tr:nth-child(even) {{
                background-color: #f2f2f2;
            }}


        </style>
    </head>
    <body>
        {extracted['article_info']}
        {extracted['guidelines']}
        {extracted['author_info']}
        {extracted['problem_notes']}
        {extracted['comments']}
        {extracted['Attachments']}
        <div class="footer-section">
            <p><strong>Journal Style_{article['jid']}</strong></p>
            <p>
                <a href="https://journals.sagepub.com/author-instructions/{article['jid']}">Preparing your manuscript @ journals.sagepub.com/author-instruction/{article['jid']}</a>
            </p>
        </div>
    </body>
    </html>
    """

    output_path = os.path.join(download_dir, article_id, f"{article_id}_merged.html")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(merged_html)

    print(f"Merged file saved at: {output_path}")



# Create a directory for downloads
download_dir = os.path.join(os.getcwd(), "downloads")
os.makedirs(download_dir, exist_ok=True)


# chrome_options = Options()
# chrome_options.add_argument("--headless=new")
# chrome_options.add_argument("--window-size=1920,1080")
# chrome_options.add_argument("--disable-gpu")
# chrome_options.add_argument("--no-sandbox")
# chrome_options.add_argument("--disable-dev-shm-usage")
# chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])

# prefs = {
#     "download.default_directory": download_dir,  # Set download directory
#     "download.prompt_for_download": False,  # Disable download prompt
#     "download.directory_upgrade": True,
#     "safebrowsing.enabled": True,  # Enable safe browsing for automatic downloads
#     "profile.default_content_settings.popups": 0,
# }
# chrome_options.add_experimental_option("prefs", prefs)

# # Initialize the Chrome driver with options
# driver = webdriver.Chrome(options=chrome_options)
# driver.execute_cdp_cmd("Page.setDownloadBehavior", {
#     "behavior": "allow",
#     "downloadPath": download_dir
# })

from selenium.webdriver.chrome.service import Service
# optionally set path to chromedriver: Service(executable_path="path/to/chromedriver")
service = Service()  

chrome_options = Options()
# remove/adjust headless if needed for debugging:
# chrome_options.add_argument("--headless=new")   # or comment out to watch the browser
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])

prefs = {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True,
    "profile.default_content_settings.popups": 0,
}
chrome_options.add_experimental_option("prefs", prefs)
options = webdriver.ChromeOptions()
options.page_load_strategy = 'eager'
# Create driver with plain selenium
driver = webdriver.Chrome(service=service, options=chrome_options)

# Allow downloads via CDP
try:
    driver.execute_cdp_cmd("Page.setDownloadBehavior", {
        "behavior": "allow",
        "downloadPath": download_dir
    })
except Exception as e:
    # on some Chrome/selenium versions this may fail; it's non-fatal
    print("Warning: Page.setDownloadBehavior failed:", e)

# increase page load timeout so slow pages don't immediately timeout
driver.set_page_load_timeout(180)

COOKIES_FILE = "sage_cookies.pkl"

def login(driver, login_id, login_pwd):
    driver.get("https://journals.sageapps.com/smart/login.aspx")
    print(f"Current URL after navigation: {driver.current_url}")
    
    # Check if cookies file exists and is not expired
    cookies_valid = False
    if os.path.exists(COOKIES_FILE):
        # Check if file is less than 30 minutes old
        file_age = time.time() - os.path.getmtime(COOKIES_FILE)
        if file_age < 1800:  # 1800 seconds = 30 minutes
            print(f"Cookie file is {file_age/60:.1f} minutes old (valid for 30 minutes)")
            try:
                with open(COOKIES_FILE, "rb") as f:
                    cookies = pickle.load(f)
                for cookie in cookies:
                    driver.add_cookie(cookie)

                # Redirect to the main page to test if session is active
                driver.get("https://journals.sageapps.com/smart/default.aspx")
                time.sleep(3)
                
                # If we're not redirected back to the login page, assume the session is valid
                if "login.aspx" not in driver.current_url:
                    print("*** Session is active - cookies are valid")
                    cookies_valid = True
                else:
                    print("* Session expired - redirected to login page")
            except Exception as e:
                print(f"Error loading cookies: {e}")
        else:
            print(f"Cookie file expired ({file_age/60:.1f} minutes old)")
            os.remove(COOKIES_FILE)
            print("Deleted expired cookie file")
    
    # If cookies aren't valid or don't exist, perform manual login
    if not cookies_valid:
        print("Performing manual login...")
        driver.get("https://journals.sageapps.com/smart/login.aspx")
        try:
            username_field = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.ID, "ctl00_SmartMasterContent_rtbuserlogin"))    
            )
            password_field = driver.find_element(By.ID, "ctl00_SmartMasterContent_rtbpasswd")

            username_field.send_keys(login_id)
            password_field.send_keys(login_pwd)
            
            # Try to find and click the sign-in button
            # Try to find and click the sign-in button safely
            try:
                sign_in_button = WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable((By.ID, "ctl00_SmartMasterContent_rblogin_input"))
                )
                sign_in_button.click()
            except TimeoutException:
                # If button not found or not clickable, try submitting with Enter key
                print("Sign in button not clickable, submitting with Enter key")
                password_field.send_keys(Keys.RETURN)


            # Wait for login to complete by checking URL change
            WebDriverWait(driver, 30).until(
                lambda d: "login.aspx" not in d.current_url
            )
            print("*** Manual login successful. Saving cookies...")

            # Save cookies for future use
            with open(COOKIES_FILE, "wb") as f:
                pickle.dump(driver.get_cookies(), f)
            
        except Exception as e:
            print(f"Login error: {e}")
            print("Current page title:", driver.title)
            print("Current URL:", driver.current_url)
            raise

try:
    # **Login**
    load_dotenv()
    login_id = os.getenv("login_id")
    login_pwd = os.getenv("login_pwd")
    login(driver, login_id, login_pwd)

    
    articles_info = []
    csv_file_path=os.path.join(os.getcwd(),"articles.csv")

    
    with open(csv_file_path,mode='r',encoding='utf-8')as csvfile:
        reader=csv.DictReader(csvfile)
        for row in reader:
            jid = row["JID"].strip()
            aid = int(row["AID"].strip())

            # 🧹 Clean up any previously downloaded files for this article
            if not clean_previous_article_data(download_dir, jid, aid):
                continue

            article = {"jid": jid, "aid": aid}
            article_id = f"{jid}{aid}"
            print(f"✅ Processing article: {article_id}")

        
        # Example article IDs
            extracted_parts={
                'guidelines':'',
                'article_info':'',
                'author_info':'',
                'problem_notes':'',
                'comments':'',
                'Attachments':''
            }
        
            article_id = f"{article['jid']}{article['aid']}"
            article_dir = f"downloads/{article_id}"
            file_name = f"{article['jid']}{article['aid']}_Unedited.docx"
            os.makedirs(article_dir, exist_ok=True)    
            
            # After login, navigate to the desired article page
            driver.get(f"https://journals.sageapps.com/smart/MaintainArticle.aspx?articleid={article['aid']}")
            time.sleep(3)
            
            # Extract and simplify HTML
            page_html = driver.page_source
            processed_html = simplified_html(page_html, f"{article['jid']}{article['aid']}.html")
            extracted_parts['article_info']=processed_html.get('article_info','')
            
            # Save simplified HTML
            # with open(os.path.join(article_dir, f"{article['jid']}{article['aid']}_simplified.html"), "w", encoding="utf-8") as file:
            #     file.write(processed_html)
            # print(f"Saved simplified HTML for article {article['aid']}")

            # Take a screenshot of the article information
            
            try:
                iframe = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "iframe"))
                )
                driver.switch_to.frame(iframe)
                print("Switched to iframe.")
            except:
                print("No iframe detected, proceeding normally.")

            # Navigate to the Attachments tab of the desired article page
            attachments_tab = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, "//span[contains(@class, 'rtsTxt') and contains(text(), 'Attachments')]"))
            )
            attachments_tab.click()
            print("✅ Successfully loaded Attachments page.")
            time.sleep(2)

            page_html=driver.page_source
            processed_html = simplified_html(page_html, f"{article['jid']}{article['aid']}_Attachments.html")
            extracted_parts["Attachments"]=processed_html.get('Attachments','')

            # Initialize tracking variables
            file_downloaded = False
            matched_file = None
            postback_matched = False
            available_files = []

            # Construct normalized article ID (used for filename matching)
            article_id = f"{article['jid']}{article['aid']}".replace("_", "").replace(" ", "").lower()

            print("🔍 Scanning for links with JavaScript postback...")

            MAX_RETRIES = 3

            for attempt in range(1, MAX_RETRIES + 1):
                try:
                    a_tags = driver.find_elements(By.TAG_NAME, "a")
                    for tag in a_tags:
                        text = tag.text.strip()
                        href = tag.get_attribute("href")

                        if not text or not href:
                            continue

                        cleaned_text = text.lower().replace(" ", "").replace("_", "")
                        if article_id in cleaned_text and "unedited" in cleaned_text and "docx" in cleaned_text and "javascript:__doPostBack" in href:
                            print(f"✅ Attempt {attempt}: Found match '{text}' triggering download...")
                            matched_file = text

                            # Trigger postback download
                            driver.execute_script("arguments[0].click();", tag)

                            # Monitor download
                            downloaded_file_path = os.path.join(download_dir, matched_file)
                            destination_path = os.path.join(article_dir, matched_file)
                            timeout = 60
                            start_time = time.time()

                            while not os.path.exists(downloaded_file_path):
                                if time.time() - start_time > timeout:
                                    print(f"⚠️ Timeout: File '{matched_file}' not found after {timeout} seconds.")
                                    break
                                time.sleep(1)

                            if os.path.exists(downloaded_file_path):
                                shutil.move(downloaded_file_path, destination_path)
                                file_downloaded = True
                                print(f"✅ File successfully downloaded and moved to: {destination_path}")
                            break  # break out of tag loop
                    if file_downloaded:
                        break  # stop retrying if success
                    else:
                        print(f"🔁 Retry {attempt} failed. Trying again...")
                        time.sleep(2)
                except StaleElementReferenceException:
                    print(f"⚠️ Retry {attempt}: StaleElementReferenceException encountered.")
                    time.sleep(2)
                except Exception as e:
                    print(f"⚠️ Retry {attempt}: Error while scanning postback links: {e}")
                    time.sleep(2)

            # Final status
            if not file_downloaded:
                print(f"❌ Failed to download unedited file for article {article_id} after {MAX_RETRIES} retries.")
            else:
                print(f"✅ Finished downloading for article: {article_id}")
    
                        
            # Take a screenshot of the guidelines tab
            try:
                guidelines_tab = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//span[contains(@class, 'rtsTxt') and contains(text(), 'Guidelines')]")
                    )
                )
                guidelines_tab.click()
                time.sleep(5)
                page_html = driver.page_source
                processed_html = simplified_html(page_html, f"{article['jid']}{article['aid']}_guidelines.html")
                extracted_parts["guidelines"]=processed_html.get('guidelines','')
                # with open(os.path.join(article_dir, f"{article['jid']}{article['aid']}_simplified_guidelines.html"), "w", encoding="utf-8") as file:
                #     file.write(processed_html)
                # print(f"Saved simplified HTML for guidelines {article['aid']}")
            except Exception as e:
                print(f"Error capturing guidelines screenshot for article {article['aid']}: {e}")

            # Navigate to the Author Info tab
            try:
                author_info_tab = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//span[@class='rtsTxt' and starts-with(text(), 'Authors')]")
                    )
                )
                author_info_tab.click()
                time.sleep(5)
                page_html = driver.page_source
                processed_html = simplified_html(page_html, f"{article['jid']}{article['aid']}_authorinfo.html")
                extracted_parts["author_info"]=processed_html.get('author_info','')
                # with open(os.path.join(article_dir, f"{article['jid']}{article['aid']}_simplified_authorinfo.html"), "w", encoding="utf-8") as file:
                #     file.write(processed_html)
                # print(f"Saved simplified HTML for author info {article['aid']}")
            except Exception as e:
                print(f"Error capturing author info screenshot for article {article['aid']}: {e}")

            # Navigate to the Problem Notes tab

            try:
    # Wait for the Problems/Notes tab and click it
                problem_notes_tab = WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//span[contains(@class, 'rtsTxt') and contains(normalize-space(.), 'Problems/Notes')]")
                    )
                )
                driver.execute_script("arguments[0].scrollIntoView(true);", problem_notes_tab)
                driver.execute_script("arguments[0].click();", problem_notes_tab)
                logging.info("✅ Clicked on Problems/Notes tab")
                time.sleep(5)
                page_html=driver.page_source
                processed_html = simplified_html(page_html, f"{article['jid']}{article['aid']}_problemnotes.html")
                extracted_parts["problem_notes"]=processed_html.get('problem_notes','')

            except Exception as e:
                logging.warning(f"⚠️ Error capturing Problem Notes for article {article['aid']}: {e}")

            try:
                comments_tab= WebDriverWait(driver,15).until(
                    EC.presence_of_element_located(
                        (By.XPATH,"//span[contains(@class,'rtsTxt') and contains(normalize-space(.), 'Comments')]")
                    )
                )    
                driver.execute_script("arguments[0].scrollIntoView(true);",comments_tab)
                driver.execute_script("arguments[0].click();",comments_tab)
                logging.info("✅ Clicked on Comments tab")
                time.sleep(5)
                page_html=driver.page_source
                processed_html = simplified_html(page_html, f"{article['jid']}{article['aid']}_comments.html")
                extracted_parts["comments"]=processed_html.get('comments','')

            except Exception as e:
                logging.warning(f"⚠️ Error capturing comments for article {article['aid']}: {e}")    


            # Merge the simplified HTML files
            
            merge_simplified_html(article_id, article, extracted_parts, download_dir)


    # Wait for the download to complete (or handle file-saving dialog if required)
    time.sleep(5)
finally:
    # Close the browser
    driver.quit()