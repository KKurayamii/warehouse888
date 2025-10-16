from django.contrib import admin
from .models import UploadedFile, QueryHistory


@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    """
    Admin interface for uploaded files.
    """
    list_display = ('filename', 'status', 'row_count', 'file_size_display', 'uploaded_at', 'uploaded_by')
    list_filter = ('status', 'uploaded_at')
    search_fields = ('filename',)
    readonly_fields = ('uploaded_at', 'file_size', 'row_count', 'processing_stats')
    date_hierarchy = 'uploaded_at'

    fieldsets = (
        ('File Information', {
            'fields': ('filename', 'file', 'file_size', 'row_count')
        }),
        ('Upload Details', {
            'fields': ('uploaded_at', 'uploaded_by', 'status')
        }),
        ('Processing', {
            'fields': ('processing_stats', 'error_message'),
            'classes': ('collapse',)
        }),
    )

    def file_size_display(self, obj):
        """Display file size in human-readable format."""
        size_bytes = obj.file_size
        if size_bytes < 1024:
            return f"{size_bytes} bytes"
        elif size_bytes < 1024 ** 2:
            return f"{size_bytes / 1024:.2f} KB"
        elif size_bytes < 1024 ** 3:
            return f"{size_bytes / (1024 ** 2):.2f} MB"
        else:
            return f"{size_bytes / (1024 ** 3):.2f} GB"

    file_size_display.short_description = 'File Size'


@admin.register(QueryHistory)
class QueryHistoryAdmin(admin.ModelAdmin):
    """
    Admin interface for query history.
    """
    list_display = ('question_preview', 'language', 'success', 'row_count', 'execution_time', 'created_at', 'created_by')
    list_filter = ('success', 'language', 'created_at')
    search_fields = ('question', 'generated_sql')
    readonly_fields = ('created_at', 'execution_time', 'row_count')
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Query', {
            'fields': ('question', 'language')
        }),
        ('SQL', {
            'fields': ('generated_sql', 'sql_explanation')
        }),
        ('Results', {
            'fields': ('success', 'row_count', 'execution_time', 'result_summary', 'error_message')
        }),
        ('Metadata', {
            'fields': ('created_at', 'created_by')
        }),
    )

    def question_preview(self, obj):
        """Display truncated question."""
        max_length = 60
        if len(obj.question) > max_length:
            return f"{obj.question[:max_length]}..."
        return obj.question

    question_preview.short_description = 'Question'
