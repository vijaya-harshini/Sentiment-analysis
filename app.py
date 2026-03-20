from flask import Flask, render_template, request, redirect
from textblob import TextBlob
import sqlite3
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

app = Flask(__name__)

# ---------------- DATABASE INIT ----------------
def init_db():
    conn = sqlite3.connect("reviews.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        text TEXT,
        sentiment TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------------- DELETE ROUTE ----------------
@app.route("/delete/<int:id>")
def delete(id):
    conn = sqlite3.connect("reviews.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM reviews WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect("/")

# ---------------- MAIN ROUTE ----------------
@app.route("/", methods=["GET", "POST"])
def index():
    result = None

    if request.method == "POST":
        text = request.form["review"]
        reviews = text.split("\n")

        pos = 0
        neg = 0
        neu = 0

        conn = sqlite3.connect("reviews.db")
        cursor = conn.cursor()

        for r in reviews:
            if r.strip() == "":
                continue

            analysis = TextBlob(r)
            polarity = analysis.sentiment.polarity

            if polarity > 0.1:
                sentiment = "Positive"
                pos += 1
            elif polarity < -0.1:
                sentiment = "Negative"
                neg += 1
            else:
                sentiment = "Neutral"
                neu += 1

            cursor.execute(
                "INSERT INTO reviews (text, sentiment) VALUES (?, ?)",
                (r, sentiment)
            )

        conn.commit()
        conn.close()

        total = pos + neg + neu if (pos + neg + neu) != 0 else 1

        result = {
            "positive": pos,
            "negative": neg,
            "neutral": neu,
            "pos_percent": round((pos/total)*100, 2),
            "neg_percent": round((neg/total)*100, 2),
            "neu_percent": round((neu/total)*100, 2)
        }

        # chart
        labels = ['Positive', 'Negative', 'Neutral']
        values = [pos, neg, neu]

        plt.figure()
        plt.bar(labels, values)
        plt.title("Sentiment Analysis Summary")

        chart_path = "static/chart.png"
        plt.savefig(chart_path)
        plt.close()

    # fetch data
    conn = sqlite3.connect("reviews.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM reviews ORDER BY id DESC")
    data = cursor.fetchall()

    conn.close()

    return render_template("index.html", result=result, data=data)



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)