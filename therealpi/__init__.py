from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from helpers import *
from datetime import datetime, timedelta

app = Flask(__name__)
client = MongoClient('localhost')
db = client.schedule
users = db.users
schedule = db.events
roommate = db.roommate


@app.route('/')
def main_page():
    return render_template("home.html", default="home")


@app.route('/calendar')
@login_required
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


@app.route('/roommates')
@login_required
def roommates():
    month = (datetime.now() - timedelta(days=1)).strftime("%B")
    search = roommate.find_one({"month": month})
    if search is None:
        new_month = (datetime.now() + timedelta(days=15)).strftime("%B")
        search = {"month": new_month, "rent": [2090, 0, 0, 0], "aaron": ["1", ""],
                  "austin": ["0", ""], "matt": ["5", ""], "ryan": ["100", ""]}
        roommate.insert_one(search)
    return render_template("roommates.html", default="roommates", info=search)


@app.route('/_update_roommate', methods=["POST"])
@login_required
def update_roommate():
    month = (datetime.now() - timedelta(days=1)).strftime("%B")
    update = dict(request.form)
    update["month"] = month
    try:
        roommate.find_one_and_replace({"month": month}, update)
        return jsonify()
    except:
        return jsonify({"error": "Couldn't update info!"})


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


@app.route('/_add_event', methods=["POST"])
def add_event():
    try:
        events = request.form.to_dict()
        events["Time"] = events.pop("Hour") + ':' + events.pop("Minute")
        events["Special Reminders"] = [events["Special Reminders"]]
        schedule.insert_one(events)
    except Exception as e:
        print(e)
        return jsonify(error="There was error")

    return jsonify(success="Event successfully added!")


if __name__ == '__main__':
    # A local variable that make testing in production possible. Set equal to false when shipped over
    in_production = False
    if in_production:
        app.secret_key = "test"
        host = ''
        debug = True
    else:
        host = '0.0.0.0'
        debug = False
    app.run(debug=debug, host=host)



