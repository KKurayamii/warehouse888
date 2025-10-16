from django.db import models
from django.contrib.auth.models import User


class UploadedFile(models.Model):
    """
    Model to track uploaded CSV files.
    """
    filename = models.CharField(max_length=255)
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    file_size = models.BigIntegerField(help_text="File size in bytes")
    row_count = models.IntegerField(default=0)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ],
        default='pending'
    )
    error_message = models.TextField(blank=True, null=True)
    processing_stats = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'Uploaded File'
        verbose_name_plural = 'Uploaded Files'

    def __str__(self):
        return f"{self.filename} ({self.uploaded_at.strftime('%Y-%m-%d %H:%M')})"


class QueryHistory(models.Model):
    """
    Model to track user queries and results.
    """
    question = models.TextField(help_text="Natural language question")
    language = models.CharField(
        max_length=5,
        choices=[('en', 'English'), ('th', 'Thai')],
        default='en'
    )
    generated_sql = models.TextField(help_text="Generated SQL query")
    sql_explanation = models.TextField(blank=True)
    result_summary = models.TextField(blank=True)
    row_count = models.IntegerField(default=0)
    execution_time = models.FloatField(help_text="Execution time in seconds", default=0)
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Query History'
        verbose_name_plural = 'Query Histories'

    def __str__(self):
        return f"{self.question[:50]}... ({self.created_at.strftime('%Y-%m-%d %H:%M')})"


class Conversation(models.Model):
    """
    Model to track chat conversations.
    """
    session_id = models.CharField(max_length=100, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Conversation'
        verbose_name_plural = 'Conversations'

    def __str__(self):
        return f"Conversation {self.session_id} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"


class ChatMessage(models.Model):
    """
    Model to store individual chat messages.
    """
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(
        max_length=10,
        choices=[
            ('user', 'User'),
            ('assistant', 'Assistant'),
            ('system', 'System')
        ]
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict, blank=True, help_text="Additional data like SQL, results, etc.")

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Chat Message'
        verbose_name_plural = 'Chat Messages'

    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."
