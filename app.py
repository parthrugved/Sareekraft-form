from flask import Flask, render_template, request
from pymongo.mongo_client import MongoClient
from datetime import datetime
import re
import os
from dotenv import load_dotenv
import certifi

load_dotenv()

app = Flask(__name__)


uri = os.environ.get("MONGO_URI")

client = MongoClient(
    uri,
    serverSelectionTimeoutMS=10000,
    tls=True,
    tlsCAFile=certifi.where()
)

db = client["sareekraft"]
collection = db["users"]


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        phone_number = request.form.get("phone-number")
        feedback = request.form.get("feedback")
        city = request.form.get("city")

        try:
            client.admin.command('ping')
            print("MongoDB connected ✅")
        except Exception as e:
            print("Mongo ERROR:", e)
  
        if not name or not email or not phone_number or not feedback or not city:
            return render_template("index.html", error="All fields are required ❌", form=request.form)

        email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(email_pattern, email):
            return render_template("index.html", error="Invalid email format ❌", form=request.form)

        if not phone_number.isdigit() or len(phone_number) != 10:
            return render_template("index.html", error="Invalid phone number ❌", form=request.form)

        if any(char.isdigit() for char in name):
            return render_template("index.html", error="Name cannot contain numbers ❌", form=request.form)

        if any(char.isdigit() for char in city):
            return render_template("index.html", error="City cannot contain numbers ❌", form=request.form)

        if any(char.isdigit() for char in feedback):
            return render_template("index.html", error="Feedback cannot contain numbers ❌", form=request.form)

        if len(feedback) < 5:
            return render_template("index.html", error="Feedback too short ❌", form=request.form)


        try:
            now = datetime.now()

            collection.insert_one({
                "name": name.strip(),
                "phone_number": phone_number,
                "email": email.strip().lower(),
                "feedback": feedback.strip(),
                "city": city.strip(),
                "timestamp": now,
                "date": now.strftime("%Y-%m-%d"),
                "time": now.strftime("%H:%M:%S")
            })
            print("✅ Data inserted successfully!")
            return render_template("index.html", success="Details submitted successfully ✅")

        except Exception as e:
            print("ERROR:", e)
            return f"Database Error: {str(e)}"

    return render_template("index.html")


if __name__ == "__main__":
    app.run()