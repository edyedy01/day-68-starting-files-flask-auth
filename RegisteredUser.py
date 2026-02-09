class RegisteredUser:
    """
    A class representing a registered user in the system.
    Follows the interface expected by Flask-Login.
    """

    def __init__(self, user_id, email, is_active=True):
        # Ensure user_id is stored as a string
        self.id = str(user_id)
        self.email = email

        # Required fields for authentication frameworks
        self.is_authenticated = True
        self.is_active = is_active
        self.is_anonymous = False

    def get_id(self):
        """
        Returns the unique identifier for the user.
        Must be a string (str).
        """
        return self.id

    def __repr__(self):
        return f"<RegisteredUser(id='{self.id}', email='{self.email}')>"

# Example Usage:
# user = RegisteredUser("user-123", "chris@example.com")
# print(f"User ID: {user.get_id()}")
# print(f"Active: {user.is_active}")