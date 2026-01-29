import os
from flask import Flask, request, render_template

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    sequence = request.form.get("sequence", "").upper()
    gc_content = round((sequence.count("G") + sequence.count("C")) / len(sequence) * 100, 2) if sequence else 0
    return render_template("result.html", sequence=sequence, gc_content=gc_content)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)