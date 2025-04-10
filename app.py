from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)
DATABASE = 'ai_articles.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
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
        WHERE lower(title) LIKE ?
           OR lower(summary) LIKE ?
        ORDER BY publication_date DESC
        LIMIT ? OFFSET ?
    """
    params = (f"%{keyword}%", f"%{keyword}%", limit, offset)

    conn = get_db_connection()
    cursor = conn.cursor()
    results = cursor.execute(query, params).fetchall()
    conn.close()

    articles = [dict(row) for row in results]
    return jsonify(articles)

@app.route("/article/<int:id>", methods=["GET"])
def get_article_by_id(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM articles WHERE id=?", (id,))
    article = cursor.fetchone()
    conn.close()
    if article:
        return jsonify(dict(article))
    return jsonify({"error": "Article not found"}), 404

if __name__ == "__main__":
    app.run(debug=True)
