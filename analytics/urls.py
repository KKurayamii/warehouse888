from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    # Frontend views
    path('', views.agent_chatbot_view, name='home'),  # Autonomous AI Agent is now the front page
    path('sales/', views.home, name='sales_analytics'),  # Old Sales Analytics chat moved here
    path('upload/', views.upload_page, name='upload_page'),

    # API endpoints
    path('api/query/', views.query_api, name='query_api'),
    path('api/chat/', views.chat_api, name='chat_api'),  # ChatGPT SQL endpoint
    path('api/code-chat/', views.code_chat_api, name='code_chat_api'),  # Code generation endpoint
    path('api/agent-chat/', views.agent_chat_api, name='agent_chat_api'),  # Autonomous agent endpoint
    path('api/upload/', views.upload_api, name='upload_api'),
    path('api/history/', views.query_history_api, name='query_history_api'),
    path('api/uploads/', views.upload_history_api, name='upload_history_api'),
    path('api/file-data/<int:file_id>/', views.file_data_api, name='file_data_api'),  # File data endpoint
    path('api/health/', views.health_check, name='health_check'),
]
