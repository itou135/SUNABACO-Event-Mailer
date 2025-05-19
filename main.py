from flask import Flask
import threading
import time
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

app = Flask(__name__)

gmail_user = os.getenv("GMAIL_USER")
app_password = os.getenv("GMAIL_APP_PASSWORD")
to_email = gmail_user

# 日本時間取得
def get_jst_now():
    return datetime.utcnow() + timedelta(hours=9)

# メール送信処理
def send_event_email():
    url = "https://sunabaco.com/event/"
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")

    seen_titles = set()
    events = soup.select("div.eventWrap > a")
    event_info_list = []

    for event in events:
        title_tag = event.find("h4", class_="eventCard__name")
        date_tag = event.find("span", class_="eventCard__date")
        link = event.get("href")

        if not title_tag or not date_tag or not link:
            continue

        title = title_tag.text.strip()
        date = date_tag.text.strip()

        if title in seen_titles:
            continue
        seen_titles.add(title)

        event_info = f"🎉 {title}\n📅 {date}\n🔗 {link}\n"
        event_info_list.append(event_info)

    if event_info_list:
        body = "今日のSUNABACOイベント情報です！\n\n" + "\n===\n".join(event_info_list)
    else:
        body = "現在、表示できるイベントは見つかりませんでした。"

    subject = "SUNABACOイベント情報（自動配信）"
    msg = MIMEMultipart()
    msg['From'] = gmail_user
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(gmail_user, app_password)
        server.send_message(msg)
        server.quit()
        print('📩 メールを送信しました！')
    except Exception as e:
        print(f'⚠️ メール送信中にエラー: {e}')

# 毎日同じ時刻にメールを送信する関数
def schedule_loop():
    target_hour = 5  # 日本時間で朝5時
    target_minute = 0
    last_sent_date = None

    while True:
        now = get_jst_now()
        current_date = now.date()

        if now.hour == target_hour and now.minute == target_minute:
            if last_sent_date != current_date:
                print(f"\n🕖 {now.strftime('%Y-%m-%d %H:%M')} にメールを送信します")
                send_event_email()
                last_sent_date = current_date
        time.sleep(30)

# Flask起動時にバックグラウンドでスケジューラ起動
@app.before_first_request
def start_scheduler():
    threading.Thread(target=schedule_loop, daemon=True).start()

@app.route('/')
def home():
    return "📡 SUNABACO Event Mailer is running!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
