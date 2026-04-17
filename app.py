from flask import Flask, render_template, request, redirect, session
import json, os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"

DATA_FILE = "tasks.json"

# ===== LOAD DATA =====
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            data = json.load(f)
            if isinstance(data, list):
                return {"tasks": data, "quote": ""}
            return data
    return {"tasks": [], "quote": ""}

# ===== SAVE DATA =====
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

# ===== LOGIN PAGE =====
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form.get("name")
        if name:
            session["user"] = name
            return redirect("/")
    return render_template("login.html")

# ===== LOGOUT =====
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")

# ===== HOME =====
@app.route("/")
def home():
    if "user" not in session:
        return redirect("/login")

    data = load_data()
    tasks = data["tasks"]
    quote = data.get("quote", "")

    search = request.args.get("search", "").lower()
    if search:
        tasks = [t for t in tasks if search in t["task"].lower()]

    total = len(tasks)
    done = len([t for t in tasks if t.get("completed")])
    percent = int((done / total) * 100) if total > 0 else 0

    today = datetime.now().strftime("%Y-%m-%d")
    pending_today = len([
        t for t in tasks
        if t.get("date") == today and not t.get("completed")
    ])

    return render_template(
        "index.html",
        tasks=tasks,
        percent=percent,
        search=search,
        pending_today=pending_today,
        quote=quote,
        now=datetime.now(),
        user=session["user"]
    )

# ===== ADD TASK =====
@app.route("/add", methods=["POST"])
def add():
    data = load_data()
    tasks = data["tasks"]

    tasks.append({
        "task": request.form.get("task"),
        "date": request.form.get("date"),
        "priority": request.form.get("priority"),
        "completed": False
    })

    save_data(data)
    return redirect("/")

# ===== COMPLETE =====
@app.route("/complete/<int:index>")
def complete(index):
    data = load_data()
    tasks = data["tasks"]

    if 0 <= index < len(tasks):
        tasks[index]["completed"] = True

    save_data(data)
    return redirect("/")

# ===== DELETE =====
@app.route("/delete/<int:index>")
def delete(index):
    data = load_data()
    tasks = data["tasks"]

    if 0 <= index < len(tasks):
        tasks.pop(index)

    save_data(data)
    return redirect("/")

# ===== SET QUOTE =====
@app.route("/set_quote", methods=["POST"])
def set_quote():
    data = load_data()
    data["quote"] = request.form.get("quote")
    save_data(data)
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)