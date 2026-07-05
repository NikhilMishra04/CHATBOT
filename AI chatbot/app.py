from flask import Flask, render_template, request, redirect, session
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from google import genai
from dotenv import load_dotenv
import sqlite3
import os

# 🔥 LOAD ENV
load_dotenv()

app = Flask(__name__)
app.secret_key = "secret123"

# 🔥 AI API TOGGLE
# False = Free ML Mode / Hardcoded logic
# True = Gemini API Mode (Fallback)
USE_API = True

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)
MODEL = "gemini-2.5-flash"

last_college = None

# 💾 DATABASE
conn = sqlite3.connect(
    "chat.db",
    check_same_thread=False
)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS chats (
    user TEXT,
    bot TEXT
)
""")

# 💾 SAVE CHAT
def save_chat(user, bot):
    cursor.execute(
        "INSERT INTO chats VALUES (?, ?)",
        (user, bot)
    )
    conn.commit()

# 🔐 LOGIN
USERNAME = "admin"
PASSWORD = "1234"

# 🏫 COLLEGE DATABASE
colleges = {
    "aktu": {
        "name": "AKTU",
        "location": "Lucknow",
        "fees": "80k/year",
        "placement": "4-6 LPA",
        "courses": "BTech, MBA, MCA",
        "hostel": "Available"
    },
    "iit delhi": {
        "name": "I I T Delhi",
        "location": "Delhi",
        "fees": "2 lakh/year",
        "placement": "20+ LPA",
        "courses": "BTech, MTech",
        "hostel": "Available"
    },
    "iit bombay": {
        "name": "I I T Bombay",
        "location": "Mumbai",
        "fees": "2.2 lakh/year",
        "placement": "25+ LPA",
        "courses": "BTech, MTech",
        "hostel": "Available"
    },
    "nit trichy": {
        "name": "N I T Trichy",
        "location": "Tamil Nadu",
        "fees": "1.5 lakh/year",
        "placement": "10-15 LPA",
        "courses": "BTech",
        "hostel": "Available"
    },
    "vit": {
        "name": "V I T Vellore",
        "location": "Tamil Nadu",
        "fees": "2 lakh/year",
        "placement": "8-10 LPA",
        "courses": "BTech, MBA",
        "hostel": "Available"
    },
    "uit rgpv shivpuri": {
        "name": "UIT RGPV Shivpuri",
        "location": "Shivpuri, MP",
        "fees": "30k/year",
        "placement": "3-5 LPA",
        "courses": "BTech",
        "hostel": "Available"
    }
}

# 🤖 ML QUESTIONS
questions = [
    "best college",
    "ai ml",
    "python",
    "engineering",
    "cse"
]

# 🤖 ML ANSWERS
answers = [
    "Top colleges include I I T Delhi, I I T Bombay and N I T Trichy.",
    "AI/ML is one of the fastest growing fields.",
    "Python is used in AI, ML and web development.",
    "Engineering provides opportunities in software and research.",
    "CSE is one of the best branches for placements."
]

# 🔑 LOGIN PAGE
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form["username"]
        pwd = request.form["password"]
        if user == USERNAME and pwd == PASSWORD:
            session["user"] = user
            return redirect("/")
        else:
            return "Invalid Login ❌"
    return render_template("login.html")

# 🔓 LOGOUT
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")

# 🏠 HOME PAGE
@app.route("/")
def home():
    if "user" not in session:
        return redirect("/login")
    return render_template("index.html")

# 🤖 CHATBOT
@app.route("/get", methods=["POST"])
def chatbot():
    global last_college
    user_input = request.form["msg"]
    text = user_input.lower()

    # 🎯 SMART RECOMMENDATION SYSTEM
    if "best college" in text:
        reply = "\n🏆 Recommended Colleges:\n\n1. IIT Delhi\n2. IIT Bombay\n3. NIT Trichy\n4. VIT Vellore\n"
        save_chat(user_input, reply)
        return reply

    # 💰 BUDGET COLLEGES
    if "budget" in text:
        reply = "\n Budget Friendly Colleges:\n\n• AKTU\n• UIT RGPV Shivpuri\n"
        save_chat(user_input, reply)
        return reply

    # 🤖 AI/ML COLLEGES
    if "ai ml" in text:
        reply = "\n Best Colleges for AI/ML:\n\n• IIT Delhi\n• IIT Bombay\n• VIT Vellore\n"
        save_chat(user_input, reply)
        return reply

    # 🏨 HOSTEL QUERY
    if "hostel" in text and "best" in text:
        reply = "\n Best Hostel Facilities:\n\n• IIT Delhi\n• VIT Vellore\n• NIT Trichy\n"
        save_chat(user_input, reply)
        return reply

    # 📈 PLACEMENT QUERY
    if "best placement" in text:
        reply = "\n Best Placement Colleges:\n\n1. IIT Bombay\n2. IIT Delhi\n3. NIT Trichy\n"
        save_chat(user_input, reply)
        return reply

    # 🔍 SMART COLLEGE SEARCH
    for clg in colleges:
        if clg in text:
            last_college = clg
            data = colleges[clg]

            # 💰 FEES
            if "fees" in text:
                reply = f"\n Fees of {data['name']}:\n{data['fees']}\n"
            # 📈 PLACEMENT
            elif "placement" in text:
                reply = f"\nPlacement of {data['name']}:\n{data['placement']}\n"
            # 📚 COURSES
            elif "course" in text:
                reply = f"\n Courses in {data['name']}:\n{data['courses']}\n"
            # 🏨 HOSTEL
            elif "hostel" in text:
                reply = f"\n Hostel in {data['name']}:\n{data['hostel']}\n"
            # 🏫 FULL INFO
            else:
                reply = f"\n College: {data['name']}\n\n Location: {data['location']}\n\n Fees: {data['fees']}\n\n Placement: {data['placement']}\n\n Courses: {data['courses']}\n\n Hostel: {data['hostel']}\n"

            save_chat(user_input, reply)
            return reply

    # 🧠 LOCAL MEMORY SYSTEM
    if last_college:
        data = colleges[last_college]
        reply = None
        if "fees" in text:
            reply = f" Fees: {data['fees']}"
        elif "placement" in text:
            reply = f" Placement: {data['placement']}"
        elif "hostel" in text:
            reply = f" Hostel: {data['hostel']}"
        elif "course" in text:
            reply = f" Courses: {data['courses']}"
        
        if reply:
            save_chat(user_input, reply)
            return reply

    # 🔵 GEMINI API FALLBACK MODE
    # If the local rules above didn't match and USE_API is True, ask Gemini!
    if USE_API:
        try:
            prompt = f"""
You are a smart AI college assistant.
Answer the user's question clearly and briefly based on your knowledge base.

User: {user_input}
"""
            response = client.models.generate_content(
                model=MODEL,
                contents=prompt
            )
            reply = response.text
            save_chat(user_input, reply)
            return reply
        except Exception as e:
            return f"Gemini API Error: {str(e)}"

    # 🤖 LOCAL ML CHATBOT FALLBACK (When USE_API = False)
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform(questions + [text])
    similarity = cosine_similarity(vectors[-1], vectors[:-1])
    index = similarity.argmax()
    score = similarity[0][index]

    if score > 0.3:
        reply = answers[index]
    else:
        reply = """
 Sorry, I couldn't understand that.
 Try asking:
• Fees of IIT Delhi
• Placement of VIT
• Hostel in AKTU
• Best AI college
• AI/ML guidance
"""
    save_chat(user_input, reply)
    return reply

# 📊 DASHBOARD
@app.route("/dashboard")
def dashboard():
    cursor.execute("SELECT * FROM chats")
    data = cursor.fetchall()
    return render_template(
        "dashboard.html",
        chats=data
    )

# ▶️ RUN PROJECT
if __name__ == "__main__":
    app.run(debug=True)