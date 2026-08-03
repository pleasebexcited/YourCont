"""
app/handlers/contact_request_handler.py: Handles the contact list and form pages

This class is the first stop when someone opens contacts list, create, detail, edit, or delete in YourCont.
It reads the browser form or contact id,
asks ContactLogicHandler to do the work for the signed in user,
then returns a template or redirect.
HTTP details stay here so they match the request handler layer on my class diagram,
and stay out of the SQL and field rules.
I keep every contact action tied to the session user id so one account cannot open or change another person's contacts.
"""

from flask import redirect, render_template, request, url_for

from app.handlers.base_request_handler import BaseRequestHandler
from app.services.contact_logic_handler import ContactLogicHandler


class ContactRequestHandler(BaseRequestHandler):

    """
    Handles contact page requests and reuses BaseRequestHandler for sessions and flash messages.
    """

    def __init__(self, contact_logic=None, auth_logic=None):

        """
        Wires ContactLogicHandler and the shared parent so login checks and contact work share one handler object.
        """

        super().__init__(auth_logic=auth_logic)
        self.contact_logic = contact_logic or ContactLogicHandler()

    def _current_user_id(self):

        """
        Reads the signed in user id from the session after require_login has already passed.

        ContactLogicHandler needs that id on every create, list, view, update, and delete call,
        so ownership stays attached to the logged in YourCont account.
        """

        user_session = self.current_session()

        return user_session.user_id if user_session else None

    def list_contacts(self):

        """
        Shows the contacts list for the signed in person only.

        routes.py sends /contacts here after require_login.
        The rows come from Postgres through ContactLogicHandler,
        then contacts.html draws the Hi Fi style list cards.
        """

        user_id = self._current_user_id()
        contacts = self.contact_logic.process_list(user_id)

        return render_template("contacts.html", contacts=contacts)

    def create_contact(self):

        """
        Shows the blank create form, or inserts a new contact when the form is posted.

        GET opens contact_form.html in create mode.
        POST asks ContactLogicHandler to validate and save the row for this user.
        After a successful save I send the person back to the contacts list with a Contact Created message,
        matching the flow I locked in the plan.
        If validation fails I show the form again with the typed values still filled in.
        """

        if request.method == "GET":
            return render_template("contact_form.html", mode="create", contact=None)

        user_id = self._current_user_id()

        try:
            ok, message, contact = self.contact_logic.process_create(user_id, request.form)
        except RuntimeError as error:
            self.flash_error(str(error))
            return render_template(
                "contact_form.html",
                mode="create",
                contact=None,
                form_values=request.form.to_dict(),
            )

        if not ok:
            self.flash_error(message)
            return render_template(
                "contact_form.html",
                mode="create",
                contact=None,
                form_values=request.form.to_dict(),
            )

        self.flash_success(message)

        return redirect(url_for("contacts"))

    def get_contact(self, contact_id):

        """
        Shows one owned contact with Edit and Delete actions.

        The contact id in the URL picks the row,
        and the session user id makes sure it belongs to this account.
        Missing or other people's contacts send the person back to the list with a short message.
        """

        user_id = self._current_user_id()
        contact = self.contact_logic.process_get(contact_id, user_id)

        if not contact:
            self.flash_error("Contact not found.")
            return redirect(url_for("contacts"))

        return render_template("contact_detail.html", contact=contact)

    def update_contact(self, contact_id):

        """
        Shows the edit form for an owned contact, or saves changes when the form is posted.

        GET fills contact_form.html from the existing Postgres row.
        POST runs the same field checks as create, then updates only if the row still belongs to this user.
        After a successful save I send the person back to the contacts list with a Contact Updated message.
        """

        user_id = self._current_user_id()
        contact = self.contact_logic.process_get(contact_id, user_id)

        if not contact:
            self.flash_error("Contact not found.")
            return redirect(url_for("contacts"))

        if request.method == "GET":
            return render_template("contact_form.html", mode="edit", contact=contact)

        try:
            ok, message, updated = self.contact_logic.process_update(
                contact_id,
                user_id,
                request.form,
            )
        except RuntimeError as error:
            self.flash_error(str(error))
            return render_template(
                "contact_form.html",
                mode="edit",
                contact=contact,
                form_values=request.form.to_dict(),
            )

        if not ok:
            self.flash_error(message)
            return render_template(
                "contact_form.html",
                mode="edit",
                contact=contact,
                form_values=request.form.to_dict(),
            )

        self.flash_success(message)

        return redirect(url_for("contacts"))

    def delete_contact(self, contact_id):

        """
        Shows the are you sure screen, or deletes the owned contact when Delete is posted.

        GET opens the Hi Fi style confirm page with the contact name.
        POST removes the row only when it belongs to the signed in user,
        then returns to the contacts list with a Contact Deleted message.
        Cancel on the page links back to detail without deleting anything.
        """

        user_id = self._current_user_id()
        contact = self.contact_logic.process_get(contact_id, user_id)

        if not contact:
            self.flash_error("Contact not found.")
            return redirect(url_for("contacts"))

        if request.method == "GET":
            return render_template("contact_delete.html", contact=contact)

        try:
            ok, message = self.contact_logic.process_delete(contact_id, user_id)
        except RuntimeError as error:
            self.flash_error(str(error))
            return redirect(url_for("contact_detail", contact_id=contact_id))

        if not ok:
            self.flash_error(message)
            return redirect(url_for("contacts"))

        self.flash_success(message)

        return redirect(url_for("contacts"))
