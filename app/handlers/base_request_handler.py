"""
app/handlers/base_request_handler.py: Shared helpers for logged in pages

Shared parent for YourCont request handlers.
My class diagram has AuthRequestHandler now, and ContactRequestHandler planned later, both inheriting from this class, so log in checks, session storage, and flash helpers live once here instead of being copied into every page handler.
"""

from functools import wraps

from flask import flash, redirect, session, url_for

from app.models.user_session import UserSession
from app.services.auth_logic_handler import AuthLogicHandler

class BaseRequestHandler:
    """
    Parent request handler that child classes reuse for sessions and short page messages.
    """

    def __init__(self, auth_logic=None):
        """
        Stores an AuthLogicHandler for session checks.

        Passing auth_logic in is useful for tests.
        Day to day use creates one here.
        """

        self.auth_logic = auth_logic or AuthLogicHandler()

    def require_login(self, view_func):
        """
        Decorator (my wrapper that sits above page function) protects a YourCont page so only signed in people can open it.

        routes.py puts this above private screens such as /contacts.
        Flask runs the check first, guests get a short message and a redirect to log in, while a valid session continues into the real page function.
        Keeping the rule here means every protected screen behaves the same.
        """

        @wraps(view_func)
        def wrapped(*args, **kwargs):
            """
            Runs before the real page. wraps keeps the original function name for debugging.
            """

            user_session = self.current_session()

            if not user_session:
                flash("Please log in to continue.")
                return redirect(url_for("login"))

            return view_func(*args, **kwargs)

        return wrapped

    def current_session(self):
        """
        Reads the signed Flask cookie session and returns a UserSession when it is still valid.
        """

        return self.auth_logic.validate_session(session.get("user"))

    def flash_error(self, message):
        """
        Queues an error message, such as a failed log in, for the next page render.
        """

        flash(message)

    def flash_success(self, message):
        """
        Queues a success message, such as account created, for the next page render.
        """

        flash(message)

    def store_session(self, user_session: UserSession):
        """
        Saves a small user dictionary into the Flask session after a successful log in.

        Only id, email, and first name go into the cookie.
        The password hash never does.
        permanent=True applies the seven day lifetime set in create_app.
        """

        session["user"] = user_session.to_dict()
        session.permanent = True

    def clear_session(self):
        """
        Removes the signed in user from the session when Logout is chosen.
        """

        session.pop("user", None)
