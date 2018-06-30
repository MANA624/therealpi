from flask import Flask, render_template, request, jsonify, sessions, session, redirect, url_for
from pymongo import MongoClient

app = Flask(__name__)
client = MongoClient('localhost')
db = client.schedule
users = db.users
schedule = db.events

app.secret_key = "super secret"

@app.route('/')
def main_page():
    return render_template("home.html", default="home")


@app.route('/calendar')
def calendar():
    return render_template("calendar.html", default="cal")


@app.route('/test')
def test():
    return render_template("test.html")


@app.route('/resume')
def resume():
    return render_template("resume.html", default="res")


@app.route('/contact')
def contact():
    return render_template("contact.html", default="contact")


@app.route('/_check_login', methods=["POST"])
def check_login():
    username = request.form["username"]
    password = request.form["password"]
    if users.find_one({"username": username, "password": password}) is not None:
        session["logged_in"] = True
        return jsonify()
    else:
        return jsonify(error="Bad credentials. Please try again")


@app.route('/_logout', methods=["GET", "POST"])
def logout():
    session.clear()
    return redirect(url_for("main_page"))


@app.route('/_add_event', methods=["GET", "POST"])
def add_event():
    events = request.form.to_dict()
    events["Time"] = events.pop("Hour") + ':' + events.pop("Minute")
    schedule.insert_one(events)

    return jsonify(error="There was error")


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')



