from flask import session, redirect, url_for
from functools import wraps


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if "logged_in" in session and session["logged_in"]:
            return f(*args, **kwargs)
        else:
            return redirect(url_for("main_page"))

    return wrap

