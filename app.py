from flask import Flask, request, jsonify
import psycopg2
import urllib.parse as urlparse

app = Flask(__name__)

# PostgreSQL credentials for Render's hosted database
DATABASE_URL = "postgresql://ai_articles_user:YbK3SjzaAYLs9nSMYa8HZP1Zd3UDxkTH@dpg-cvsbflur433s73c32psg-a.oregon-postgres.render.com/ai_articles"

# Parse the database URL to get the individual credentials
url = urlparse.urlparse(DATABASE_URL)

DB_PARAMS = {
    'dbname': url.path[1:],  # Extract the database name (remove the leading '/')
    'user': url.username,
    'password': url.password,
    'host': url.hostname,
    'port': url.port
}

def get_db_connection():
    conn = psycopg2.connect(**DB_PARAMS)
    return conn

@app.route("/")
def home():
    return {"message": "AI News API is running"}

@app.route("/articles", methods=["GET"])
def get_articles():
    keyword = request.args.get("keyword", "").lower()
    limit = int(request.args.get("limit", 10))
    offset = int(request.args.get("offset", 0))

    query = """
        SELECT * FROM articles
        WHERE lower(title) LIKE %s
           OR lower(summary) LIKE %s
        ORDER BY publication_date DESC
        LIMIT %s OFFSET %s
    """
    params = (f"%{keyword}%", f"%{keyword}%", limit, offset)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    results = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    conn.close()

    articles = [dict(zip(columns, row)) for row in results]
    return jsonify(articles)

@app.route("/article/<int:id>", methods=["GET"])
def get_article_by_id(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM articles WHERE id=%s", (id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        columns = [desc[0] for desc in cursor.description]
        return jsonify(dict(zip(columns, row)))
    return jsonify({"error": "Article not found"}),
