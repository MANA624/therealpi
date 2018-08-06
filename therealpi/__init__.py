from flask import Flask, render_template, request, session, redirect, url_for, abort, send_file, safe_join, \
    flash, Response, jsonify
from pymongo import MongoClient, DESCENDING
from passlib.hash import pbkdf2_sha256
from datetime import datetime, timedelta
from functools import wraps
import os.path
from bson.objectid import ObjectId
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

app = Flask(__name__)
client = MongoClient('localhost')
db = client.schedule
jobs = db.jobs
users = db.users
schedule = db.events
roommate = db.roommate
server = smtplib.SMTP('smtp.gmail.com', 587)

"""
    BEGIN BLOCK: HELPER FUNCTIONS
"""


def my_flash(msg_type, title, content):
    flash(msg_type + ':' + title + ':' + content)


def send_mail(name, sender_address, subject, body):
    config_data = app.config["EMAIL"]
    fromaddr = config_data["email_from"]
    toaddr = config_data["email_to"]
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = subject
    msg.add_header('reply-to', sender_address)

    body = body + "\n\n" + "Name: " + name + "\nSender address: " + sender_address
    msg.attach(MIMEText(body, 'plain'))

    server.starttls()
    server.login(fromaddr, config_data["email_password"])
    text = msg.as_string()
    server.sendmail(sender_address, toaddr, text)
    server.quit()


"""
    END SECTION: HELPER FUNCTIONS
"""
"""
    BEGIN SECTION: REQUIRED LOGINS
"""


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if "logged_in" in session:
            if "admin" in session or "employer" in session:
                return f(*args, **kwargs)
            else:
                abort(403)
        else:
            abort(401)
    return wrap


def roommate_required_post(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if "logged_in" in session:
            if "roommate" in session:
                return f(*args, **kwargs)
            else:
                return Response("You don't have the privileges to do that!", status=403)
        else:
            return Response("You are not logged in", status=401)
    return wrap


def admin_required_post(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if "logged_in" in session:
            if "admin" in session:
                return f(*args, **kwargs)
            else:
                return Response("You don't have the privileges to do that!", status=403)
        else:
            return Response("You are not logged in", status=401)
    return wrap

"""
    END SECTION: REQUIRED LOGINS
"""
"""
    BEGIN SECTION: TEMPLATE RENDERING
"""


@app.route('/')
def main_page():
    return render_template("home.html", default="home")


@app.route('/resume')
def resume():
    listings = []
    try:
        for listing in jobs.find().sort([("order", DESCENDING)]):
            listings.append(listing)
    except Exception as e:
        print(e)
    return render_template("resume.html", default="res", listings=listings)


@app.route('/contact')
def contact():
    return render_template("contact.html", default="contact")


@app.route('/roommates')
@login_required
def roommates():
    month = (datetime.now() - timedelta(days=2)).strftime("%B")
    search = roommate.find_one({"month": month})
    if search is None:
        new_month = (datetime.now() + timedelta(days=15)).strftime("%B")
        search = {"month": new_month, "rent": [2090, 0, 0, 0], "aaron": ["1", ""],
                  "austin": ["0", ""], "matt": ["5", ""], "ryan": ["100", ""]}
        roommate.insert_one(search)
    my_flash("info", "Notice!", "Please save any changes so others can see!")
    return render_template("roommates.html", default="roommates", info=search)


@app.route('/calendar')
@login_required
def calendar():
    date_today = datetime.today().strftime("%Y-%m-%d")
    events_raw = schedule.find()
    events = []
    for doc in events_raw:
        new_doc = {
            "title": doc["title"] + ': ' + doc["more_info"],
            "start": doc["datetime"].strftime("%Y-%m-%dT%H:%M:00"),
            "id": doc["_id"]
        }
        events.append(new_doc)
    return render_template("calendar.html", default="cal", date=date_today, events=events)


@app.route('/admin')
@login_required
def admin():
    return render_template("admin.html", default="admin")

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


@app.route('/_check_login', methods=["POST"])
def check_login():
    username = request.form["username"]
    password = request.form["password"]
    user = users.find_one({"username": username})
    if user and pbkdf2_sha256.verify(password, user["password"]):
        session["logged_in"] = True
        for privilege in user["other"]:
            session[privilege] = True
        my_flash("success", "Login Success!", "Welcome " + username + '!')
        return Response()
    else:
        return Response("Bad credentials. Please try again", status=401)


@app.route('/_logout', methods=["GET", "POST"])
def logout():
    session.clear()
    return redirect(url_for("main_page"))


@app.route('/_send_email', methods=["POST"])
def send_email():
    try:
        email = request.form.to_dict()
        send_mail(email["name"], email["email"], email["subject"], email["message"])
    except Exception as e:
        print(e)
        return Response("There was an error sending the email", status=503)
    return Response("Email sent!")


@app.route('/_update_roommate', methods=["POST"])
@roommate_required_post
def update_roommate():
    month = (datetime.now() - timedelta(days=1)).strftime("%B")
    update = request.form.to_dict(flat=False)
    update["month"] = month
    try:
        roommate.find_one_and_replace({"month": month}, update)
        return Response("Successfully updated info")
    except:
        return Response("Couldn't update information in database", status=503)


@app.route('/_add_event', methods=["POST"])
@admin_required_post
def add_event():
    try:
        event = request.form.to_dict()
        date = [int(x) for x in event.pop("date").split('/')]
        event["datetime"] = datetime(year=date[2], month=date[0], day=date[1], hour=int(event.pop("hour")),
                                     minute=int(event.pop("minute")))
        event["send_text"] = event["send_text"] == "true"
        schedule.insert_one(event)
    except Exception as e:
        print(e)
        return Response("Could not create an event!", status=503)
    send_dict = {
        'title': event['title'] + ':' + event["more_info"],
        'start': event["datetime"].strftime("%Y-%m-%dT%H:%M:00"),
        '_id': str(event["_id"])
    }
    return jsonify(message="You successfully created an event", event=send_dict)


@app.route('/_delete_event', methods=["POST"])
@admin_required_post
def delete_event():
    try:
        id = request.form["_id"]
        result = schedule.delete_one({"_id": ObjectId(id)})
        if not result.deleted_count:
            raise NameError("No object with that id found!")
    except Exception as e:
        print(e)
        return Response("Could not delete that event!", status=503)
    return Response("You successfully deleted that event")


@app.route('/_create_user', methods=["POST"])
@admin_required_post
def create_user():
    try:
        user = dict(request.form)
        user['password'] = pbkdf2_sha256.encrypt(user['password'][0])
        user['other'].remove('')
        user['username'] = user['username'][0]
        users.insert_one(user)
    except Exception as e:
        print(e)
        return Response("There was an error accessing the database", status=503)
    return Response("User successfully created!")


@app.route('/_create_job', methods=["POST"])
@admin_required_post
def create_job():
    try:
        job = request.form.to_dict()
        if jobs.find().count() > 0:
            max_job = jobs.find_one(sort=[("order", -1)])["order"] + 5
        else:
            max_job = 10
        job["order"] = max_job
        jobs.insert_one(job)
    except Exception as e:
        print(e)
        return Response("There was an error accessing the database", status=503)
    return Response("Job successfully created!")

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


@app.errorhandler(401)
def unauthorized(e):
    return render_template('401.html'), 401


@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403

"""
    END SECTION: ERROR HANDLING
"""


if __name__ == '__main__':
    host = '0.0.0.0'
    app.run(host=host)
