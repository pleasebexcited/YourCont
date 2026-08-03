"""
app/handlers/auth_request_handler.py: Handles the sign up, log in, and log out pages

This class is the first stop when someone opens sign up, log in, or log out in YourCont.
It reads the browser form, asks AuthLogicHandler to create or check an account,
then returns a template or redirect.
HTTP details stay here so they match the request handler layer on my class diagram,
and stay out of the password rules.
"""

from flask import redirect, render_template, request, url_for

from app.handlers.base_request_handler import BaseRequestHandler
from app.services.auth_logic_handler import AuthLogicHandler

class AuthRequestHandler(BaseRequestHandler):

    """
    Handles auth page requests and reuses BaseRequestHandler for sessions and flash messages.
    """

    def __init__(self, auth_logic=None):

        """
        Wires AuthLogicHandler into the shared parent so login checks and form work share one object.
        """

        super().__init__(auth_logic=auth_logic or AuthLogicHandler())

    def signup(self):

        """
        Shows the sign up form, or creates a YourCont account from the posted fields.

        If our user's account creation is successful redirects to log in.
        A validation or database problem will show the form again with a flash message and the values already typed,
        so people do not start from a blank page after a small mistake.
        This is important for my plan for creating an application that almost anyone can use.
        """

        # Someone already signed in should not see sign up again.

        if self.current_session():
            return redirect(url_for("contacts"))

        if request.method == "GET":
            return render_template("signup.html")

        try:
            ok, message = self.auth_logic.register_user(
                first_name=request.form.get("first_name"),
                last_name=request.form.get("last_name"),
                email=request.form.get("email"),
                password=request.form.get("password"),
            )
        except RuntimeError as error:

            # Missing DATABASE_URL becomes a page message instead of a Flask crash screen.

            self.flash_error(str(error))
            return self._signup_form_with_values()

        if not ok:
            self.flash_error(message)
            return self._signup_form_with_values()

        self.flash_success(message)
        return redirect(url_for("login"))

    def _signup_form_with_values(self):

        """
        Re opens signup.html with the posted names and email still filled in.
        Password is left blank on purpose after a failed attempt.
        """

        return render_template(
            "signup.html",
            first_name=request.form.get("first_name", ""),
            last_name=request.form.get("last_name", ""),
            email=request.form.get("email", ""),
        )

    def login(self):

        """
        Shows the log in form, or checks the posted email and password.

        A valid result stores a UserSession in the cookie and sends the person to contacts.
        A failed result keeps the email field filled so only the password needs retyping.
        """

        if self.current_session():
            return redirect(url_for("contacts"))

        if request.method == "GET":
            return render_template("login.html")

        try:
            user, error = self.auth_logic.authenticate(
                email=request.form.get("email"),
                password=request.form.get("password"),
            )
        except RuntimeError as error:

            # Same DATABASE_URL guard as sign up, shown on the log in card.

            self.flash_error(str(error))
            return render_template("login.html", email=request.form.get("email", ""))

        if error:
            self.flash_error(error)
            return render_template("login.html", email=request.form.get("email", ""))

        user_session = self.auth_logic.create_session(user)
        self.store_session(user_session)

        return redirect(url_for("contacts"))

    def logout(self):

        """
        Clears cookie session data and returns the person to the log in page.
        """

        self.clear_session()
        return redirect(url_for("login"))
