# 🧠 AI News Scraper & API (Flask + Selenium)

A simple web scraping and API project that fetches the latest AI-related news articles from [Artificial Intelligence News](https://www.artificialintelligence-news.com/), stores them in SQLite, and provides a Flask-based API for keyword-based search.

---

## 📂 Project Structure

```
/your-flask-app
    ├── app.py              # Your main Flask app file
    ├── requirements.txt    # Your Python dependencies
    ├── Procfile            # The Procfile (without any extension)
    └── other-files         # Any other files your app needs

```

---

## 🚀 Features

- Scrapes articles (title, URL, publication date, summary)
- Stores data in SQLite
- Keyword-based article search via Flask API
- Ready for local use or deployment on Render/Vercel/etc.
- Includes Postman collection for testing

---

## 🔧 Requirements

- Python 3.7+
- Google Chrome / Edge
- [Selenium WebDriver](https://www.selenium.dev/documentation/webdriver/getting_started/install_drivers/)

---

## 📦 Installation

```bash
git clone https://github.com/yourusername/ai-news-scraper.git
cd ai-news-scraper
pip install -r requirements.txt
```

Update the path to the WebDriver in `scraper.py`:

```python
Service(executable_path='path_to_your_webdriver')
```

---

## 📰 Run the Scraper

```bash
python scraper.py
```

Choose how many articles to fetch → data will be saved to `ai_articles.db`.

---

## 🖥️ Run the Flask App (Local)

```bash
python app.py
```

API will be available at: [http://localhost:5000](http://localhost:5000)

---

## 📡 API Endpoints

| Method | Endpoint          | Description                        |
|--------|-------------------|------------------------------------|
| GET    | `/articles`       | Get all articles                   |
| GET    | `/search?q=term`  | Search articles by keyword         |
| GET    | `/article/{id}`   | Get article by ID                  |

You can test these using **Postman** — import `postman_collection.json`.

---

## 🌐 Deployment

You can deploy the Flask app for free using:

### 🟡 Render

1. Create a new Web Service
2. Connect to your GitHub repo
3. Set `Start Command` as:

```bash
gunicorn app:app
```

4. Use `requirements.txt` for dependencies

### ⚠️ Note:

- If you're scraping dynamically, Render/Vercel might not support WebDriver execution — consider scraping locally or scheduling it via cron and pushing data to the deployed app.
- For live scraping + deployment, consider **PythonAnywhere** or a **VPS**.

---

## 📹 Optional Demo Video

[📺 YouTube Demo Link] *(If available)*

---

## 📁 Postman Collection

Use the included `postman_collection.json` to test your endpoints locally or after deployment.

---

## 👨‍💻 Author

- **Your Name**
- GitHub: [@yourusername](https://github.com/yourusername)

---

## 📝 License

MIT License
