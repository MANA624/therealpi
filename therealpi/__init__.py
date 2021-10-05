from flask import Flask, render_template, request, session, redirect, url_for, abort, send_file, safe_join, \
    flash, Response, jsonify
from werkzeug.utils import secure_filename
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
from twilio.request_validator import RequestValidator
from twilio.twiml.messaging_response import MessagingResponse
# from Crypto.Cipher import AES
from time import sleep
from subprocess import call
from random import choice
import imghdr


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
sharon = db.sharon
texts = db.texts
iv = "G4XO4L\X<J;MPPLD"

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
# def decrypt_message(message, session_key):
#     cipher = AES.new(session_key, AES.MODE_CBC, iv)
#     return cipher.decrypt(message).decode().strip()

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


def sharon_login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if "logged_in" in session:
            if "admin" in session or "sharon" in session:
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


def sharon_required_post(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if "logged_in" in session:
            if "sharon" in session:
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
    # my_flash("warning", "Notice!", "Therealpi.net is undergoing summer improvements, \\"
    #                                "and I don't have a lot of time to work on it, so some "
    #                                "things may be broken for a while. Sorry!")
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
    messages = texts.find()

    # Sort the messages
    messages = list(messages)
    messages = sorted(messages, key=lambda x: x["date"], reverse=True)

    # Properly format the date
    def stringify(message):
        message["date"] = message["date"].strftime("%m/%d/%Y, %H:%M")
        return message
    messages = list(map(stringify, messages))

    # Split into two groups
    num_msgs_on_top = 10
    messages1 = messages[:num_msgs_on_top]
    messages2 = messages[num_msgs_on_top:]
    return render_template("texting.html", messages1=messages1, messages2=messages2, default="text")


@app.route('/admin')
@admin_login_required
def admin():
    # Sharon stuff
    pics = os.listdir(safe_join(app.root_path, 'static/uploads'))
    # print(url_for('static', filename="uploads/Sharon.JPG"))
    # End Sharon stuff

    return render_template("admin.html", default="admin", pics=pics)
















@app.route('/sharon2')
@sharon_login_required
def sharon_page():
    # form = PostForm()
    phase, next_day = get_phase()
    additional_info = {}
    if phase == '10':
        sequences = [
            "2 3 9 7 4 1 16 8 15 5 6 21 22 18 10 11 19 17 14 12 23 25 24 13 20",
            "1 17 14 25 3 2 16 4 11 5 7 13 9 8 15 6 12 19 20 10 21 22 18 23 24",
            "2 7 9 4 8 21 12 3 13 10 6 1 24 14 5 11 15 16 20 23 17 22 18 19 25",
            "1 7 2 3 4 6 8 13 10 5 12 22 9 17 20 11 18 25 24 15 21 14 16 23 19",
            "1 2 5 10 15 6 7 9 3 18 8 11 14 24 19 17 22 20 4 25 16 12 21 13 23",
            "7 17 2 3 4 11 6 19 9 5 1 23 14 13 15 16 18 12 10 8 21 22 24 25 20",
            "3 4 9 6 10 25 1 21 14 20 11 12 7 13 5 17 22 2 15 24 16 23 18 8 19"
        ]
        additional_info["sequence"] = choice(sequences)
        # additional_info["sequence"] = "1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 25 24"  # Test

    return render_template("sharon.html", phase=phase, additional_info=additional_info, next_day=next_day)


@app.route("/_submit_challenge", methods=["POST"])
@sharon_login_required
def submit_challenge():
    details = request.form.to_dict()
    database_json = sharon.find_one({"metadata": True})
    # Structure: {'$challenge': [$day, '$cipher', $ideal_count]
    ciphers = {'2': [1, "tqXQkB4D", 1], '4': [2, "8fBRCpgp", 1], '6': [3, "Fox44R9Jt", 1]}
    # Structure: {'$challenge': [$day, $idealProgress]}
    trivials = {'1': [1, 0], '5': [3, 0], '7': [3, 2]}

    # Trivial challenges: the sliding puppy and getting dressed
    if details["challenge"] in trivials:
        day = trivials[details["challenge"]][0]
        ideal_progress = trivials[details["challenge"]][1]
        if database_json["phase"][day] == ideal_progress:
            increment_phase(day)
        else:
            return Response("It appears you already completed the challenge!", status=500)
    # Handles all of the cipher challenges
    elif details["challenge"] in ciphers:
        challenge = details["challenge"]
        submitted_cipher = details["cipher"]
        day = ciphers[challenge][0]
        actual_cipher = ciphers[challenge][1]
        ideal_progress = ciphers[challenge][2]
        if database_json["phase"][day] == ideal_progress:
            if submitted_cipher == actual_cipher:
                increment_phase(day)
            else:
                return Response("Incorrect cipher!!!", status=500)
        else:
            return Response("It appears you already completed the challenge!", status=500)
    # The quiz about you challenge
    elif details["challenge"] == '3':
        if database_json["phase"][2] != 0:
            return Response("It appears you already completed the challenge!", status=500)
        score = 0
        answers = {
            "color1": "black",
            'color2': "purple",
            "date": "01/12/2019",
            "twenty_op": "11/19/2018",
            "pearl": "12/13/2018",
            "aisle": "aisle",
            "isle": "isle",
            "buttons": "buttons",
        }
        for answer in answers:
            if answers[answer] == details[answer].lower():
                score += 1
        total = len(answers)
        # Didn't get a perfect score
        if score != total:
            return Response("You scored {0} out of {1}. Keep trying!".format(score, total), status=500)
        # Did get a perfect score
        increment_phase(2)
    else:
        return Response("I'm... you... what? How did you get here?", status=500)
    return Response("Challenge complete! Refresh the page for next steps!")


def get_phase():
    # TODO: Convert to EST
    day_begins = []

    # day_begins.append(datetime.now() - timedelta(days=2, hours=1))  # Nov 18
    day_begins.append(datetime(year=2020, month=11, day=18, hour=15, minute=30))  # Nov 18 @ 5:30EST
    day_begins.append(day_begins[0] + timedelta(days=1))  # Nov 19 @ 5:30 EST
    day_begins.append(day_begins[1] + timedelta(hours=21, minutes=45))  # Nov 20 @ 3:15PM EST
    day_begins.append(day_begins[2] + timedelta(days=9999))

    curr_time = datetime.now()
    day = 0
    while curr_time > day_begins[day]:
        day += 1

    # increment_phase(amount=1)
    # reset_phase()
    data = sharon.find_one({"metadata": True})
    phase = data['phase'][day]

    max_challenges = [0, 2, 2, 2]
    if phase < max_challenges[day]:
        next_time = None
    else:
        # Convert to EST
        day_begins[day] += timedelta(hours=2)
        # if day_begins[day+1].day == datetime.now().day:
        #     print("same")
        if day_begins[day].strftime("%d") == datetime.now().strftime("%d"):
            today_tomorrow = "today"
        else:
            today_tomorrow = "tomorrow"

        next_time = today_tomorrow + ', ' + day_begins[day].strftime("%x at %I:%M %p") + " EST"
        # Convert back to MST
        day_begins[day] -= timedelta(hours=2)

    return str(day) + str(phase), next_time


def increment_phase(day, amount=1):
    data = sharon.find_one({"metadata": True})
    data["phase"][day] += amount
    sharon.find_one_and_replace({"metadata": True}, data)


@app.route("/_reset_challenges", methods=["POST"])
@admin_required_post
def reset_phase():
    data = sharon.find_one({"metadata": True})
    data["phase"] = [0, 0, 0, 0]
    sharon.find_one_and_replace({"metadata": True}, data)
    return Response("All challenges were reset")


def allowed_file(filename):
    ALLOWED_EXTENSIONS = ['jpg', 'png']
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def validate_image(stream):
    header = stream.read(512)
    stream.seek(0)
    format = imghdr.what(None, header)
    format = format.lower()
    if not format:
        return None
    return '.' + (format if format != 'jpeg' else 'jpg')


@csrf.exempt
@sharon_required_post
@app.route('/_submit_photo', methods=['POST'])
def upload_files():
    if "file" not in request.files or request.files['file'].filename == '':
        my_flash("danger", "Upload Not Successful", "File was not included")
        return redirect(url_for('sharon_page'))
    uploaded_file = request.files['file']
    filename = secure_filename(uploaded_file.filename)
    filename = filename.lower()
    if filename != '':
        file_ext = os.path.splitext(filename)[1]
        # Generate new sharon.xxx file
        i = 1
        filename = "sharon" + str(i) + file_ext
        while os.path.exists(safe_join(app.root_path, url_for('static', filename="uploads/" + filename)[1:])):
            i += 1
            filename = "sharon" + str(i) + file_ext
        if not allowed_file(filename):
            return Response("Not an allowed file extension!", status=500)
        # if file_ext != validate_image(uploaded_file.stream):
        #     return Response("Couldn't validate the file!", status=500)
        path = safe_join(app.root_path, url_for('static', filename="uploads/" + filename)[1:])
        uploaded_file.save(path)
    my_flash("success", "Upload Successful!", "Refresh often to check for approval!")
    return redirect(url_for('sharon_page'))











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
@sharon_required_post
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
        texts.insert({"sender": "Matt", "body": msg, "date": datetime.now()})

    except Exception as e:
        log_error(e)
        return Response("There was an error!", status=500)
    return Response("The text was sent successfully!")


@app.route('/_recv_text', methods=["GET"])  # POST throws an error?!
def recv_text():
    try:
        # TODO: Authenticate
        text_config = app.config["TEXT"]
        info = dict(request.args)
        # Everything is a list of a single string for some reason
        for key in info:
            info[key] = info[key][0]
        headers = dict(request.headers)

        if "X-Twilio-Signature" not in headers:
            raise KeyError("No X-Twilio-Signature key found in request %s", str(headers))
        twilio_sig = headers["X-Twilio-Signature"]

        validator = RequestValidator(text_config["auth_token"])
        url = request.url
        if not validator.validate(url, None, twilio_sig):  # GET needs no POST params...
            # db.debug.insert({"url": url, "twilio_sig": twilio_sig})
            raise KeyError("Incorrect X-Twilio-Signature used!!")

        if info["From"] == text_config["my_num"]:
            sender = "Matt"
        elif info["From"] == text_config["sharon_num"]:
            sender = "Sharon"
        else:
            sender = info["From"]

        texts.insert({"sender": sender, "body": info["Body"], "date": datetime.now()})

    except Exception as e:
        log_error(e)
        return abort(404)
    # On success, send a response message
    resp = MessagingResponse()
    resp.message("The message was processed successfully!")
    return str(resp)


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
