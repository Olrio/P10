from django.core.exceptions import ValidationError


class ContainsLetterValidator:
    """
    Validate whether the password contains alpha characters.
    """

    def validate(self, password, user=None):
        if not any(char.isalpha() for char in password):
            raise ValidationError(
                "This password must contain at least one letter",
                code="password_no_letter",
            )

    def get_help_text(self):
        return "Your password must contain at least one letter"


class ContainsNumberValidator:
    """
    Validate whether the password contains decimal characters.
    """

    def validate(self, password, user=None):
        if not any(char.isdecimal() for char in password):
            raise ValidationError(
                "This password must contain at least one number",
                code="password_no_number",
            )

    def get_help_text(self):
        return "Your password must contain at least one number"
