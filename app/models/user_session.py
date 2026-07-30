"""
app/models/user_session.py: Stores who is currently logged in

Small logged in state for YourCont after a successful sign in.
It only keeps user id, email, and first name, which is enough for the header and later ownership checks.
The password hash never goes into the cookie.
AuthLogicHandler creates it; BaseRequestHandler saves and clears it.
"""

class UserSession:
    """
    Values I keep while someone is signed into YourCont.
    """

    def __init__(self, user_id, email, first_name):
        """
        Stores only what protected pages need from the signed in person.
        """

        self.user_id = user_id
        self.email = email
        self.first_name = first_name

    def to_dict(self):
        """
        Converts this object into a dictionary Flask can place in the signed cookie session.
        """

        return {
            "user_id": self.user_id,
            "email": self.email,
            "first_name": self.first_name,
        }

    @classmethod
    def from_dict(cls, data):
        """
        Rebuilds a UserSession from cookie data, or returns None when the data is missing.
        """

        if not data:
            return None

        return cls(
            user_id=data.get("user_id"),
            email=data.get("email"),
            first_name=data.get("first_name"),
        )
