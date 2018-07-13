from flask import Flask, render_template, request, jsonify, session, redirect, url_for, abort, send_file, safe_join
from pymongo import MongoClient
from passlib.hash import sha256_crypt
from datetime import datetime, timedelta
from functools import wraps
import os.path

app = Flask(__name__)
client = MongoClient('localhost')
db = client.schedule
users = db.users
schedule = db.events
roommate = db.roommate


"""
    BEGIN BLOCK: HELPER FUNCTIONS
"""


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if "logged_in" in session and session["logged_in"]:
            return f(*args, **kwargs)
        else:
            abort(403)

    return wrap


def roommate_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if "logged_in" in session and session["roommate"]:
            return f(*args, **kwargs)
        else:
            abort(403)

    return wrap


"""
    END SECTION: HELPER FUNCTIONS
"""
"""
    BEGIN SECTION: TEMPLATE RENDERING
"""


@app.route('/')
def main_page():
    return render_template("home.html", default="home")


@app.route('/calendar')
@login_required
def calendar():
    return render_template("calendar.html", default="cal")


@app.route('/admin')
def admin():
    return render_template("admin.html", default="admin")


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
@roommate_required
def roommates():
    month = (datetime.now() - timedelta(days=1)).strftime("%B")
    search = roommate.find_one({"month": month})
    if search is None:
        new_month = (datetime.now() + timedelta(days=15)).strftime("%B")
        search = {"month": new_month, "rent": [2090, 0, 0, 0], "aaron": ["1", ""],
                  "austin": ["0", ""], "matt": ["5", ""], "ryan": ["100", ""]}
        roommate.insert_one(search)
    return render_template("roommates.html", default="roommates", info=search)


"""
    END SECTION: TEMPLATE RENDERING
"""
"""
    BEGIN SECTION: DOWNLOADS
"""


@app.route("/return_file/<filename>")
def return_file(filename):
    path = safe_join(app.root_path, url_for('static', filename="downloads/"+filename)[1:])
    if os.path.isfile(path):
        return send_file(path)
    else:
        abort(404)

"""
    END SECTION: DOWNLOADS
"""
"""
    BEGIN SECTION: AJAX REQUESTS
"""


@app.route('/_update_roommate', methods=["POST"])
@login_required
def update_roommate():
    month = (datetime.now() - timedelta(days=1)).strftime("%B")
    update = request.form.to_dict(flat=False)
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
    user = users.find_one({"username": username})
    if sha256_crypt.verify(password, user["password"]):
        session["logged_in"] = True
        for privilege in user["other"]:
            session[privilege] = True
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


@app.route('/_create_user', methods=["POST"])
def create_user():
    try:
        print(request)
        user = dict(request.form)
        user['password'] = sha256_crypt.encrypt(user['password'][0])
        user['other'].remove('')
        user['username'] = user['username'][0]
        print(user)
        users.insert_one(user)
    except Exception as e:
        print(e)
        return jsonify(error="There was error")
    return jsonify()


"""
    END SECTION: AJAX REQUESTS
"""

"""
    BEGIN SECTION: ERROR HANDLING
"""


@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500


@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403

"""
    END SECTION: ERROR HANDLING
"""


if __name__ == '__main__':
    # A local variable that make testing in development possible. Set equal to false when shipped over
    in_development = True
    if in_development:
        app.secret_key = "test"
        host = ''
        debug = True
    else:
        host = '0.0.0.0'
        debug = False
    app.run(debug=debug, host=host)
