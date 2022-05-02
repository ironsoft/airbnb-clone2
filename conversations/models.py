from django.db import models
from core.models import TimeStampedModel


class Conversation(TimeStampedModel):

    """Conversation Model Definition"""

    participants = models.ManyToManyField(
        "users.User", related_name="conversations", blank=True
    )

    def __str__(self):
        usernames = []
        users = self.participants.all()
        for user in users:
            usernames.append(user.username)
        return ", ".join(usernames)

    def count_messages(self):
        return self.messages.count()

    count_messages.short_description = "Number of Messages"

    def count_participants(self):
        return self.participants.count()

    count_participants.short_description = "Number of Participants"


class Message(TimeStampedModel):

    """Message Model Definition"""

    message = models.TextField()
    user = models.ForeignKey(
        "users.User", related_name="messages", on_delete=models.CASCADE
    )
    conversation = models.ForeignKey(
        "Conversation", related_name="messages", on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.user} says: {self.message}"

    def last_updated(self):
        return self.updated

    last_updated.short_description = "Lastest Updated"
