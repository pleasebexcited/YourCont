"""
app/routes.py: Maps each web address to the right page or handler

This file is the URL map for YourCont.
Each route connects a web address to a handler method or template so page behaviour follows my class diagram instead of piling into one giant script.
Sign up, log in, and log out already talk to Postgres.
Contact screens still show sample data until I build real create, update, and delete, but they already require a logged in session through AuthRequestHandler.
"""

from flask import render_template

from app.handlers.auth_request_handler import AuthRequestHandler


def register_routes(app):

    """
    THis will register every YourCont page with Flask when the app starts.

    This tells Flask which web address opens which screen. e.g. login for log in or contacts for the contacts list, so a browser request can reach the right handler or template.

    Handler objects are created once here and reused.
    That matches how my request handler layer is drawn and keeps routes.py focused on addresses rather than form logic.
    """

    auth_handler = AuthRequestHandler()

    @app.route("/")
    def home():

        """
        Opens the site root.
        Guests see the log in screen, people who are already signed in get sent on to contacts by auth_handler.login.
        """

        return auth_handler.login()

    @app.route("/login", methods=["GET", "POST"])
    def login():

        """
        Serves the log in page, or checks email and password when the form is submitted.
        """

        return auth_handler.login()

    @app.route("/signup", methods=["GET", "POST"])
    def signup():

        """
        Serves the sign up page, or creates an account when the form is submitted.
        After a successful sign up the handler sends the person back to log in.
        """

        return auth_handler.signup()

    @app.route("/logout", methods=["GET", "POST"])
    def logout():

        """
        Clears the signed in session and returns the person to the log in page.
        """

        return auth_handler.logout()

    @app.route("/contacts")
    @auth_handler.require_login
    def contacts():

        """
        Shows the contacts list after require_login has confirmed a valid session.
        The Jane and Michael rows are temporary placeholders from my Hi Fi so I can check the layout before Postgres contact tables exist.
        """

        # Temporary list data only. Real rows owned by the logged in user come later.
        sample_contacts = list(_SAMPLE_CONTACTS.values())

        return render_template("contacts.html", contacts=sample_contacts)

    @app.route("/contacts/new")
    @auth_handler.require_login
    def contact_new():

        """
        Opens a blank create contact form for someone who is already logged in.
        """

        return render_template("contact_form.html", mode="create", contact=None)

    @app.route("/contacts/<int:contact_id>")
    @auth_handler.require_login
    def contact_detail(contact_id):

        """
        Shows one contact with Edit and Delete actions underneath the fields.
        """

        contact = _sample_contact(contact_id)

        return render_template("contact_detail.html", contact=contact)

    @app.route("/contacts/<int:contact_id>/edit")
    @auth_handler.require_login
    def contact_edit(contact_id):

        """
        Opens the shared contact form with sample values filled in for editing.
        """

        contact = _sample_contact(contact_id)

        return render_template("contact_form.html", mode="edit", contact=contact)

    @app.route("/contacts/<int:contact_id>/confirm-delete")
    @auth_handler.require_login
    def contact_delete(contact_id):

        """
        Shows the are you sure screen before a contact would be removed.
        """

        contact = _sample_contact(contact_id)

        return render_template("contact_delete.html", contact=contact)


# Temporary Hi Fi sample contacts used by the list, detail, edit, and delete screens until real Postgres contact rows exist.
_SAMPLE_CONTACTS = {
    1: {
        "id": 1,
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "jane@example.com",
        "phone": "021 456 7890",
        "address": "12 Example St, Auckland",
        "birthday": "2001-01-01",
        "birthday_display": "01/01/2001",
        "relationship": "Work",
        "notes": "Notes",
    },
    2: {
        "id": 2,
        "first_name": "Michael",
        "last_name": "Brown",
        "email": "michael@example.com",
        "phone": "027 555 1234",
        "address": "45 Queen St, Auckland",
        "birthday": "1995-06-15",
        "birthday_display": "15/06/1995",
        "relationship": "Friend",
        "notes": "Notes",
    },
}


def _sample_contact(contact_id):

    """
    Returns the matching Hi Fi sample contact for detail, edit, and delete.
    Falls back to Jane if the id is unknown, until real Postgres contact rows replace this.
    """

    return _SAMPLE_CONTACTS.get(contact_id, _SAMPLE_CONTACTS[1])
