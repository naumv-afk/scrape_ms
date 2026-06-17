import os
from playwright.sync_api import sync_playwright
import smtplib
from email.message import EmailMessage
import time

# משיכת משתני הסביבה
URL = os.environ.get("JOB_URL")
EMAIL_SENDER = os.environ.get("EMAIL_SENDER")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.environ.get("EMAIL_RECEIVER")

def check_for_job():
    try:
        print("Launching browser via Playwright...")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            print(f"Navigating to URL: {URL}")
            page.goto(URL, timeout=60000)

            all_pages_text = ""
            page_number = 1

            while True:
                print(f"--- Processing Page {page_number} ---")
                page.wait_for_load_state("networkidle")
                time.sleep(3)

                current_page_text = page.inner_text("body").lower()
                all_pages_text += "\n" + current_page_text
                print(f"Page {page_number}: Extracted {len(current_page_text)} characters.")

                next_button = page.get_by_role("button", name="Next").or_(page.locator('[aria-label*="Next"]')).first

                if next_button.is_visible() and next_button.is_enabled():
                    print(f"Next button found. Clicking to move to page {page_number + 1}...")
                    next_button.scroll_into_view_if_needed()
                    next_button.click()
                    page_number += 1
                    time.sleep(3)
                else:
                    print("No more pages found. Exiting pagination loop.")
                    break

            # מילות המפתח אופסו למטרה המקורית
            keywords = ["student", "intern", "internship"]
            
            found_keywords = [kw for kw in keywords if kw in all_pages_text]
            
            if found_keywords:
                print(f"Match found! Keywords: {found_keywords}. Sending email...")
                send_email(found_keywords)
            else:
                print("No matching roles found. Safe to ignore.")

            browser.close()
            
    except Exception as e:
        print(f"An error occurred during scraping: {e}")

def send_email(found_keywords):
    msg = EmailMessage()
    msg.set_content(f"A relevant student/intern role was detected at Microsoft Careers:\n\nLink: {URL}\n\nKeywords matched: {', '.join(found_keywords)}")
    
    msg['Subject'] = 'Job Alert: Student/Intern position found at Microsoft Israel!'
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
        smtp.send_message(msg)

if __name__ == "__main__":
    check_for_job()
