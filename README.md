# 📰 News Aggregator – Flask RSS App

A Python + Flask application that aggregates and displays real-time news from various RSS feeds. Built as part of my university project and deployed temporarily using Ngrok for live demonstration.

## 🚀 Features
- Pulls live news using `feedparser`
- Filters by category and keyword
- Clean UI with Bootstrap
- Fast loading via `flask_caching`
- Temporarily deployed using Ngrok

## 🔧 How to Run Locally

```bash
pip install -r requirements.txt
python app.py

Then in a separate terminal:

bash
Copy
Edit
ngrok http 5000


