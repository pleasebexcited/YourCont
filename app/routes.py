"""
app/routes.py: Maps each web address to the right page or handler

This file is the URL map for YourCont.
Each route connects a web address to a handler method or template so page behaviour follows my class diagram,
instead of piling into one giant script.
Sign up, log in, and log out talk to Postgres through AuthRequestHandler.
Contact create, list, view, update, and delete talk to Postgres through ContactRequestHandler for the signed in user only.
"""

from app.handlers.auth_request_handler import AuthRequestHandler
from app.handlers.contact_request_handler import ContactRequestHandler


def register_routes(app):

    """
    THis will register every YourCont page with Flask when the app starts.

    This tells Flask which web address opens which screen.
    e.g. login for log in or contacts for the contacts list,
    so a browser request can reach the right handler or template.

    Handler objects are created once here and reused.
    That matches how my request handler layer is drawn and keeps routes.py focused on addresses rather than form logic.
    """

    auth_handler = AuthRequestHandler()
    contact_handler = ContactRequestHandler()

    @app.route("/")
    def home():

        """
        Opens the site root.
        Guests see the log in screen,
        people who are already signed in get sent on to contacts by auth_handler.login.
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
        Shows the sign up page, or creates an account when the form is submitted.
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
    @contact_handler.require_login
    def contacts():

        """
        Shows the contacts list for the signed in user after require_login has confirmed a valid session.
        ContactRequestHandler loads only this person's Postgres rows for the Hi Fi style cards.
        """

        return contact_handler.list_contacts()

    @app.route("/contacts/new", methods=["GET", "POST"])
    @contact_handler.require_login
    def contact_new():

        """
        Opens a blank create contact form, or saves a new contact when the form is posted.
        A successful create returns to the contacts list with a Contact Created message.
        """

        return contact_handler.create_contact()

    @app.route("/contacts/<int:contact_id>")
    @contact_handler.require_login
    def contact_detail(contact_id):

        """
        Shows one owned contact with Edit and Delete actions underneath the fields.
        The number in the URL is the contact id in Postgres for that row.
        """

        return contact_handler.get_contact(contact_id)

    @app.route("/contacts/<int:contact_id>/edit", methods=["GET", "POST"])
    @contact_handler.require_login
    def contact_edit(contact_id):

        """
        Opens the shared contact form for an owned contact, or saves edits when the form is posted.
        A successful update returns to the contacts list with a Contact Updated message.
        """

        return contact_handler.update_contact(contact_id)

    @app.route("/contacts/<int:contact_id>/confirm-delete", methods=["GET", "POST"])
    @contact_handler.require_login
    def contact_delete(contact_id):

        """
        Shows the are you sure screen, or deletes the owned contact when Delete is posted.
        A successful delete returns to the contacts list with a Contact Deleted message.
        """

        return contact_handler.delete_contact(contact_id)
