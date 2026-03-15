class PersonaChatbotError(Exception):
    """Base exception for the application."""


class NotFoundError(PersonaChatbotError):
    """Base exception for not-found entities."""
