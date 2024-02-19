from django.db import models
from django.db.models import JSONField

class Conversation(models.Model):
    email = models.EmailField()
    time_spent = models.IntegerField(help_text="Time spent in conversation, in seconds")
    chat_log = JSONField(help_text="JSON structure containing the chat log")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation with {self.email} on {self.created_at}"
