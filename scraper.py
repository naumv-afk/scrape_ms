import os
from playwright.sync_api import sync_playwright
import smtplib
from email.message import EmailMessage
import time

# משיכת משתני הסביבה (נשאר ללא שינוי)
URL = os.environ.get("JOB_URL")
EMAIL_SENDER = os.environ.get("EMAIL_SENDER")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.environ.get("EMAIL_RECEIVER")

def check_for_job():
    try:
        print("Launching browser via Playwright...")
        with sync_playwright() as p:
            # הפעלת Chromium במצב ללא גרפיקה (headless)
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # ניווט ל-URL והגדלת ה-Timeout ל-60 שניות (אתרים אלו איטיים)
            print(f"Navigating to URL: {URL}")
            page.goto(URL, timeout=60000)

            # פתרון לאתרים דינמיים: המתנה שהעמוד ייטען לחלוטין ושלבקשות הרשת יסתיימו
            print("Waiting for dynamic content to load...")
            page.wait_for_load_state("networkidle")
            
            # המתנה נוספת קצרה של 5 שניות לביטחון
            time.sleep(5)

            # הוצאת כל הטקסט הקריא מה-Body של העמוד והמרתו לאותיות קטנות
            print("Extracting page text...")
            page_text = page.inner_text("body").lower()
            print(f"Extracted {len(page_text)} characters.")

            # מילות המפתח לחיפוש (אותיות קטנות בלבד)
            keywords = ["software developer student", "intern"]
            
            # בדיקה האם אחת מהמילים קיימת בטקסט שחולץ
            found_keywords = [kw for kw in keywords if kw in page_text]
            
            if found_keywords:
                print(f"Match found! Keywords: {found_keywords}. Sending email...")
                send_email(found_keywords)
            else:
                print("No matching roles found in the dynamic content.")

            browser.close()
            
    except Exception as e:
        print(f"An error occurred during scraping: {e}")

# פונקציית שליחת המייל נשארת כמעט אותו דבר
def send_email(found_keywords):
    msg = EmailMessage()
    # הוספתי כותרת קצת יותר ברורה למקרה של מיקרוסופט
    msg.set_content(f"A relevant role was detected at Microsoft Microsoft Careers:\n\nLink: {URL}\n\nKeywords matched: {', '.join(found_keywords)}")
    
    msg['Subject'] = 'Job Alert: Student/Intern position found at Microsoft Israel!'
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
        smtp.send_message(msg)

if __name__ == "__main__":
    check_for_job()
