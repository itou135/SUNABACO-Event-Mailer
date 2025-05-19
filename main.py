from flask import Flask
import os
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import threading
import time

app = Flask(__name__)

# ✅ Gmail設定（環境変数から取得）
gmail_user = os.getenv("GMAIL_USER")
app_password = os.getenv("GMAIL_APP_PASSWORD")
to_email = gmail_user  # 自分宛に送信

# ✅ JST時間取得
def get_jst_now():
    return datetime.utcnow() + timedelta(hours=9)

# ✅ メール送信関数
def send_event_email():
    url = "https://sunabaco.com/event/"
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")

    seen_titles = set()
    events = soup.select("div.eventWrap > a")
    event_info_list = []

    for event in events:
        title_tag = event.find("h4", class_="eventCard__name")
        date_tag = event.find("span", class_="
