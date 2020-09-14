from flask import Flask, render_template, request, session, redirect, url_for, abort, send_file, safe_join, \
    flash, Response, jsonify
from pymongo import MongoClient, DESCENDING
from passlib.hash import pbkdf2_sha256
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from functools import wraps
import os.path
from bson.objectid import ObjectId
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask_wtf.csrf import CSRFProtect, CSRFError
import sendgrid
from sendgrid.helpers.mail import Email, Content, Mail
import ssl
from twilio.rest import Client
from Crypto.Cipher import AES
from time import sleep
from subprocess import call


app = Flask(__name__)
csrf = CSRFProtect()
csrf.init_app(app)
WTF_CSRF_TIME_LIMIT = None
client = MongoClient('localhost')
db = client.schedule
jobs = db.jobs
users = db.users
schedule = db.events
roommate = db.roommate
iv = "G4XO4L\X<J;MPPLD"
proxy_path = "/var/www/therealpi/therealpi/proxy/"

"""
    BEGIN BLOCK: HELPER FUNCTIONS
"""


# Flashes a message to the user through Flask's flash system
def my_flash(msg_type, title, content):
    flash(msg_type + ':' + title + ':' + content)


# Sends an email to me, the administrator
def send_mail(name, sender_address, subject, body):
    config_data = app.config["EMAIL"]
    fromaddr = config_data["email_from"]
    toaddr = config_data["email_to"]
    # msg = MIMEMultipart()
    # msg['From'] = fromaddr
    # msg['To'] = toaddr
    # msg['Subject'] = subject
    # msg.add_header('reply-to', sender_address)

    body = body + "\n\n" + "Name: " + name + "\nSender address: " + sender_address
    # msg.attach(MIMEText(body, 'plain'))

    # server = smtplib.SMTP('smtp.gmail.com', 587)
    # server.starttls()
    # server.login(fromaddr, config_data["email_password"])
    # text = msg.as_string()
    # server.sendmail(sender_address, toaddr, text)
    # server.quit()

    sg = sendgrid.SendGridAPIClient(apikey=config_data["sendgrid_key"])
    from_email = Email("matt@therealpi.net")
    to_email = Email("pivotman624@gmail.com")
    content = Content("text/html", body)
    mail = Mail(from_email, subject, to_email, content)
    response = sg.client.mail.send.post(request_body=mail.get())


# This is just a function to make sure that I'm not putting unexpected values from the AJAX request
# into my database. Shouldn't be necessary under normal use
def check_dict(old_dict, keys):
    if all(key in old_dict for key in keys):
        new_dict = {key: sanitize(old_dict[key]) for key in keys}
        return new_dict
    else:
        return False


def log_error(e):
    print(e)


# Sanitizing input in Python and MongoDB usually isn't that big of a deal,
# but just to be safe we'll take away all capabilities that can be found through
# a NoSQL injection
def sanitize(user_input):
    if type(user_input) != str:
        return user_input
    user_input = user_input.replace('$', '')
    user_input = user_input.replace('{', '')
    user_input = user_input.replace('}', '')
    return user_input


def get_datetime(date, hour, minute):
    return datetime(year=date[2], month=date[0], day=date[1], hour=int(hour), minute=int(minute))


def pad_message(message):
    return message + " "*((16-len(message))%16)


# Decrypts the message using AES. Same as server function
def decrypt_message(message, session_key):
    cipher = AES.new(session_key, AES.MODE_CBC, iv)
    return cipher.decrypt(message).decode().strip()

"""
    END SECTION: HELPER FUNCTIONS
"""
"""
    BEGIN SECTION: REQUIRED LOGINS
"""


def admin_login_required(f):
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


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
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
    my_flash("warning", "Notice!", "Therealpi.net is undergoing summer improvements, \\"
                                   "and I don't have a lot of time to work on it, so some "
                                   "things may be broken for a while. Sorry!")
    if session and "just_logged_in" in session and session["just_logged_in"]:
        session["just_logged_in"] = False
        my_flash("success", "Login Success!", "Welcome " + session["username"] + '!')
    return render_template("home.html", default="home")


@app.route('/employer')
def employer():
    return redirect(url_for('check_login', username="employer", password="hireme123"))


@app.route('/resume')
def resume():
    listings = []
    try:
        for listing in jobs.find().sort([("order", DESCENDING)]):
            listings.append(listing)
    except Exception as e:
        log_error(e)
    return render_template("resume.html", default="res", listings=listings)


@app.route('/contact')
def contact():
    return render_template("contact.html", default="contact")


@app.route('/roommates')
@login_required
def roommates():
    month = (datetime.now() - timedelta(days=2)).strftime("%B")
    search = {}
    try:
        search = roommate.find_one({"month": month})
        if search is None:
            new_month = (datetime.now() + timedelta(days=15)).strftime("%B")
            search = {"month": new_month, "rent": [2300, 0, 0, 0], "aaron": ["", ""],
                      "michael": ["", ""], "matt": ["", ""], "ryan": ["", ""]}
            roommate.insert_one(search)
        my_flash("success", "Notice!", "You rock!")
    except Exception as e:
        log_error(e)
        abort(500)
    return render_template("roommates.html", default="roommates", info=search)


@app.route('/calendar')
@admin_login_required
def calendar():
    date_today = datetime.today().strftime("%Y-%m-%d")
    events = []
    try:
        events_raw = schedule.find({"owner": session["username"]})
        # events_raw = schedule.find()
        for doc in events_raw:
            new_doc = {
                "title": doc["title"] + ': ' + doc["more_info"],
                "start": doc["datetime"].strftime("%Y-%m-%dT%H:%M:00"),
                "id": doc["_id"]
            }
            events.append(new_doc)
    except Exception as e:
        log_error(e)
    return render_template("calendar.html", default="cal", date=date_today, events=events)


@app.route('/texting')
@admin_login_required
def texting():
    return render_template("texting.html", default="text")


@app.route('/admin')
@admin_login_required
def admin():
    try:
        status_file = proxy_path + "status"
        with open(status_file) as reader:
            status = reader.read()
            status = int(status)
        if not status:
            status_text = "off"
        elif status == 1:
            status_text = "on"
        else:
            status_text = "unknown"
    except Exception as e:
        status_text = "unknown"
    return render_template("admin.html", default="admin", status=status_text)


"""
    END SECTION: TEMPLATE RENDERING
"""
"""
    BEGIN SECTION: DOWNLOADS
"""


@csrf.exempt
@app.route("/return_file/<filename>", methods=["GET", "POST"])
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


@app.route('/_check_login', methods=["GET", "POST"])
def check_login():
    try:
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]
        elif request.method == "GET":
            username = request.args.get("username")
            password = request.args.get("password")
    except Exception as e:
        log_error(e)
        return Response("Could not get username or password", status=500)
    try:
        user = users.find_one({"username": username})
        if user and pbkdf2_sha256.verify(password, user["password"]):
            session["logged_in"] = True
            session["just_logged_in"] = True
            session["username"] = username
            for privilege in user["other"]:
               session[privilege] = True
            return redirect(url_for("main_page"))
        else:
            return Response("Bad credentials. Please try again", status=401)
    except Exception as e:
        log_error(e)
        return Response("Credentials generated an error.", status=500)


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
        log_error(e)
        return Response("There was an error sending the email", status=500)
    return Response("Email sent!")


@app.route('/_update_roommate', methods=["POST"])
@roommate_required_post
def update_roommate():
    month = (datetime.now() - timedelta(days=1)).strftime("%B")
    try:
        update = request.form.to_dict(flat=False)
        update = check_dict(update, ("rent", "ryan", "aaron", "matt", "michael"))
        if not update:
            return Response("Not all required fields were sent", status=400)
        update["month"] = month
        roommate.find_one_and_replace({"month": month}, update)
        return Response("Successfully updated info")
    except Exception as e:
        log_error(e)
        return Response("Couldn't update information in database", status=500)


@app.route('/_add_event', methods=["POST"])
@admin_required_post
def add_event():
    try:
        event = request.form.to_dict()

        event = check_dict(event, ("title", "more_info", "date", "hour", "minute", "send_text", "freq", "end_date"))
        if not event:
            return Response("Not all required fields were sent", status=400)
        date = [int(x) for x in event["date"].split('/')]
        current_date = get_datetime(date, event["hour"], event["minute"])
        event["send_text"] = event["send_text"] == "true"
        event["owner"] = session["username"]
        frequency = event["freq"]

        if frequency == "once":
            end_datetime = current_date
        else:
            end_date = [int(x) for x in event["end_date"].split('/')]
            end_datetime = get_datetime(end_date, event["hour"], event["minute"])

        for key in ["date", "hour", "minute", "freq", "end_date"]:
            event.pop(key)

        while current_date <= end_datetime:
            if "_id" in event:
                event.pop("_id")
            event["datetime"] = current_date
            schedule.insert_one(event)
            if frequency == "weekly":
                delta = timedelta(days=7)
            elif frequency == "bi-week":
                delta = timedelta(days=14)
            elif frequency == "monthly":
                delta = relativedelta(months=1)
            else:
                break
            current_date += delta

    except Exception as e:
        log_error(e)
        return Response("Could not create an event!", status=500)
    send_dict = {
        'title': event['title'] + ':' + event["more_info"],
        'start': event["datetime"].strftime("%Y-%m-%dT%H:%M:00"),
        '_id': str(event["_id"])
    }
    return jsonify(message="You successfully created an event", event=send_dict), 201


@app.route('/_delete_event', methods=["POST"])
@admin_required_post
def delete_event():
    try:
        id = request.form["_id"]
        result = schedule.delete_one({"_id": ObjectId(id)})
        if not result.deleted_count:
            raise NameError("No object with that id found!")
    except Exception as e:
        log_error(e)
        return Response("Could not delete that event!", status=500)
    return Response("You successfully deleted that event")


@app.route('/_send_text', methods=["POST"])
@admin_required_post
def send_text():
    try:
        text_config = app.config["TEXT"]
        info = request.form
        event = check_dict(info, ("msg", "recipient"))
        msg = event["msg"]
        recipient = event["recipient"]
        if recipient == "matt":
            num = text_config["my_num"]
        elif recipient == "sharon":
            num = text_config["sharon_num"]
        else:
            return Response("No such recipient found!", status=500)

        twilio_cli = Client(text_config["SID"], text_config["auth_token"])

        # body = "Don't bother. I can't help you with your homework"
        message = twilio_cli.messages.create(body=msg,
                                             from_=text_config["twilio_num"],
                                             to=num)

    except Exception as e:
        log_error(e)
        return Response("There was an error!", status=500)
    return Response("The text was sent successfully!")


@app.route('/_call_self', methods=["POST"])
@admin_required_post
def call_self():
    try:
        text_config = app.config["TEXT"]
        client = Client(text_config["SID"], text_config["auth_token"])

        call = client.calls.create(
            to=text_config["my_num"],
            from_=text_config["twilio_num"],
            url="http://demo.twilio.com/docs/voice.xml"
        )
    except Exception as e:
        log_error(e)
        return Response("Could not call yourself!", status=500)
    return Response("Call going through now!")


@app.route('/_create_user', methods=["POST"])
@admin_required_post
def create_user():
    try:
        user = dict(request.form)
        user = check_dict(user, ("username", "password", "other"))
        if not user:
            return Response("Not all required fields were sent", status=400)
        user['password'] = pbkdf2_sha256.encrypt(user['password'])
        # user['other'].remove('')
        user['username'] = user['username']
        users.insert_one(user)
    except Exception as e:
        log_error(e)
        return Response("There was an error accessing the database", status=500)
    return Response("User successfully created!"), 201


@app.route('/_proxy_switch', methods=["POST"])
@admin_required_post
def proxy_switch():
    manager_file = "proxyManager.sh"
    try:
        action_dict = dict(request.form)
        action_dict = check_dict(action_dict, ("is_enable",))
        action_dict["is_enable"] = action_dict["is_enable"][0]
        if action_dict["is_enable"] == 'true':
            action = "start"
        else:
            action = "stop"
        retcode = call([proxy_path+manager_file, action])
        if retcode == 0:
            if action == "start":
                status = "on"
            else:
                status = "off"
        else:
            status = "unknown"
    except Exception as e:
        log_error(e)
        return Response("There was an error changing the proxy", status=500)
    return jsonify(message="Proxy switched!", status=status), 201


@app.route('/_create_job', methods=["POST"])
@admin_required_post
def create_job():
    try:
        job = request.form.to_dict()
        job = check_dict(job, ("heading", "dates_worked", "job_title", "job_description"))
        if not job:
            return Response("Not all required fields were sent", status=400)
        if jobs.find().count() > 0:
            max_job = jobs.find_one(sort=[("order", -1)])["order"] + 5
        else:
            max_job = 10
        job["order"] = max_job
        jobs.insert_one(job)
    except Exception as e:
        log_error(e)
        return Response("There was an error accessing the database", status=500)
    return Response("Job successfully created!"), 201


@app.route('/_edit_job', methods=["POST"])
@admin_required_post
def edit_job():
    try:
        job = request.form.to_dict()
        job = check_dict(job, ("old_title", "job_title", "dates_worked", "heading", "order", "job_description"))
        if not job:
            return Response("Not all required fields were sent", status=400)
        if jobs.find({"job_title": job["old_title"]}).count() == 0:
            return Response("No job with that title", status=400)
        final_dict = {}
        for key in job:
            if key != "old_title" and job[key]:
                final_dict[key] = job[key]
        if "order" in final_dict:
            final_dict["order"] = int(final_dict["order"])
        print(final_dict)
        jobs.update({"job_title": job["old_title"]}, {"$set": final_dict})
    except Exception as e:
        log_error(e)
        return Response("There was an error accessing the database", status=500)
    return Response("Job successfully edited!"), 201


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


@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    return Response("Bad CSRF token!"), 400

"""
    END SECTION: ERROR HANDLING
"""


if __name__ == '__main__':
    host = '0.0.0.0'
    app.run(host=host)
