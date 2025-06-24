from flask import Flask, render_template, request
import os
from utils.logic import inject_journal, generate_payload, post_to_qbo

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        file = request.files["file"]
        path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(path)

        df = inject_journal(path)
        if df.empty:
            return "<h3>⚠️ No data found in the journal entry.</h3>")
        payload = generate_payload(df)
        status, response = post_to_qbo(payload)

        return f"<h3>📤 QBO Push Done</h3><p>Status: {status}</p><pre>{response}</pre>"

    return render_template("upload.html")

if __name__ == "_main_":
    app.run(debug=True,port=8000)