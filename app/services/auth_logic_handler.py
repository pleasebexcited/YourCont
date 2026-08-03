"""
app/services/auth_logic_handler.py: Account rules for signing up and logging in

Sign up and log in rules for YourCont live here so routes and request handlers stay thin.
Field checks, password hashing with Werkzeug web application library,
and building a UserSession all happen in this class.
Plain password text never goes into Postgres, only a hash is stored.
I am using Werkzeug for YourCont as it already comes with Flask,
and gives me safe password hashing and checking without needing to additional unneccessary security code.
"""

from werkzeug.security import check_password_hash, generate_password_hash

from app.models.user_session import UserSession
from app.services.user_database_handler import UserDatabaseHandlerRds

class AuthLogicHandler:

    """
    Account rules used by AuthRequestHandler when someone registers or signs in.
    """

    def __init__(self, user_db=None):

        """
        Attaches the users table helper.
        A different user_db can be passed in later for tests without needing a live database.
        """

        self.user_db = user_db or UserDatabaseHandlerRds()

    def register_user(self, first_name, last_name, email, password):

        """
        Validates sign up fields, hashes the password, and inserts a new users row.

        Returns True with a success message when the account is created,
        or False with an error message when something is wrong.
        AuthRequestHandler turns that into a redirect or shows the form again.
        """

        first_name = (first_name or "").strip()
        last_name = (last_name or "").strip()
        email = (email or "").strip().lower()
        password = password or ""

        if not first_name or not last_name or not email or not password:
            return False, "Please fill in all fields."

        # Eight characters will just be for MVP launch,
        # I wiil improve validation/security post deployment in future sprints.

        if len(password) < 8:
            return False, "Password must be at least 8 characters."

        # Each email can only own one YourCont account.

        if self.user_db.select_user_by_email(email):
            return False, "An account with that email already exists."

        password_hash = generate_password_hash(password)
        self.user_db.insert_user(first_name, last_name, email, password_hash)

        return True, "Account created. Please log in."

    def authenticate(self, email, password):

        """
        Checks email and password against the users table.

        A match returns the User object.
        A miss returns a single generic error so I do not reveal whether the email or the password was wrong.
        """

        email = (email or "").strip().lower()
        password = password or ""

        user = self.user_db.select_user_by_email(email)

        if not user or not check_password_hash(user.password_hash, password):
            return None, "Email or password is incorrect."

        return user, None

    def create_session(self, user):

        """
        Builds the small UserSession stored in the Flask cookie after a successful log in.
        """

        return UserSession(
            user_id=user.user_id,
            email=user.email,
            first_name=user.first_name,
        )

    def validate_session(self, session_data):

        """
        Turns cookie data back into a UserSession, or None when the data is missing or incomplete.
        """

        user_session = UserSession.from_dict(session_data)

        if not user_session or not user_session.user_id:
            return None

        return user_session
