import os
import requests
from bs4 import BeautifulSoup
import smtplib
from email.message import EmailMessage

# משיכת משתני הסביבה מתוך GitHub Secrets
URL = os.environ.get("JOB_URL")
EMAIL_SENDER = os.environ.get("EMAIL_SENDER")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD") # App Password, לא סיסמה רגילה
EMAIL_RECEIVER = os.environ.get("EMAIL_RECEIVER")

def check_for_job():
    try:
        # שליחת בקשה ל-URL
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(URL, headers=headers)
        response.raise_for_status()
        
        # ניתוח ה-HTML והוצאת הטקסט
        soup = BeautifulSoup(response.text, 'html.parser')
        page_text = soup.get_text().lower()
        
        # מילות המפתח לחיפוש (מומרות לאותיות קטנות כדי למנוע בעיות Case Sensitivity)
        keywords = ["software developer student", "intern"]
        
        # בדיקה האם אחת מהמילים קיימת בטקסט של העמוד
        found_keywords = [kw for kw in keywords if kw in page_text]
        
        if found_keywords:
            print(f"Match found! Keywords: {found_keywords}. Sending email...")
            send_email(found_keywords)
        else:
            print("No matching roles found this time.")
            
    except Exception as e:
        print(f"An error occurred: {e}")

def send_email(found_keywords):
    msg = EmailMessage()
    msg.set_content(f"Target role detected at {URL}\n\nKeywords matched: {', '.join(found_keywords)}")
    
    msg['Subject'] = 'Job Alert: Student/Intern position found!'
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER

    # התחברות לשרת ה-SMTP של גוגל ושליחת המייל
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
        smtp.send_message(msg)

if __name__ == "__main__":
    check_for_job()
