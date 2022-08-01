from django.core.exceptions import ValidationError


class ContainsLetterValidator:
    """
    Validate whether the password contains alpha characters.
    """

    @staticmethod
    def validate(password, user=None):
        if not any(char.isalpha() for char in password):
            raise ValidationError(
                "This password must contain at least one letter",
                code="password_no_letter",
            )

    @staticmethod
    def get_help_text():
        return "Your password must contain at least one letter"


class ContainsNumberValidator:
    """
    Validate whether the password contains decimal characters.
    """

    @staticmethod
    def validate(password, user=None):
        if not any(char.isdecimal() for char in password):
            raise ValidationError(
                "This password must contain at least one number",
                code="password_no_number",
            )

    @staticmethod
    def get_help_text():
        return "Your password must contain at least one number"
