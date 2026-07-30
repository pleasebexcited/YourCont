"""
app/__init__.py: Builds and sets up the Flask app

I created this file to put the YourCont website together.
create_app loads my private settings from .env, points Flask at the templates and CSS folders,
sets the log in cookie rules, turns on form protection, then connects every page address from routes.py.
application.py calls create_app so the site starts the same way on my PC and later on Elastic Beanstalk.
"""

import os
from datetime import timedelta

from dotenv import load_dotenv
from flask import Flask
from flask_wtf import CSRFProtect


# csrf is created once at import time, then attached inside create_app.
# It blocks other sites from posting to my log in or sign up forms using someone else's browser.
csrf = CSRFProtect()


def create_app():
    """
    Builds a ready Flask app for YourCont and returns it.

    Paths, secrets, cookie flags, CSRF, and routes are all wired here so application.py only needs to call create_app().
    That keeps startup in one place for local work and AWS.
    """

    # templates/ and static/ sit in the project root, not inside the app package.
    # Building paths from this file means Flask still finds them if I start the app from another folder.
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    # Loading .env from the project folder (with override) means SECRET_KEY and DATABASE_URL win even when the terminal inherited an empty value from Windows.
    load_dotenv(os.path.join(base_dir, ".env"), override=True)

    app = Flask(
        __name__,
        template_folder=os.path.join(base_dir, "templates"),
        static_folder=os.path.join(base_dir, "static"),
    )

    # Flask signs the session cookie with SECRET_KEY so logged in state cannot be forged.
    # The "or" fallback covers a missing key and an empty string in the environment.
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY") or "dev-only-change-me"

    # HttpOnly means page JavaScript cannot read the session cookie.
    app.config["SESSION_COOKIE_HTTPONLY"] = True

    # SameSite Lax means the log in cookie is not freely sent when other websites try to use it.
    # It is still sent when someone opens YourCont through a normal link, so day to day use still works.
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    # Secure cookies only travel over HTTPS. Off for localhost, on for Elastic Beanstalk.
    app.config["SESSION_COOKIE_SECURE"] = os.getenv("SESSION_COOKIE_SECURE", "0") == "1"

    # Seven days keeps reception staff from re entering passwords every hour during a shift.
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=7)

    csrf.init_app(app)

    # Routes come last so every config value is ready before the first browser request.
    from app.routes import register_routes

    register_routes(app)

    return app
